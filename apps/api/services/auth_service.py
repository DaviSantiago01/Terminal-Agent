from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import hmac
import secrets

from app.db import (
    create_auth_session,
    get_auth_session_by_token_hash,
    get_user_by_email,
    get_user_by_id,
    revoke_auth_session_by_token_hash,
)

DEFAULT_AUTH_SESSION_TTL_HOURS = 24


class InvalidCredentialsError(Exception):
    """Credenciais invalidas para login."""


class InvalidSessionError(Exception):
    """Sessao ausente, expirada ou revogada."""


@dataclass
class AuthenticatedIdentity:
    user_id: int
    email: str
    role: str
    is_active: bool
    created_at: datetime


@dataclass
class LoginResult:
    session_token: str
    expires_at: datetime
    identity: AuthenticatedIdentity


def hash_password(password: str) -> str:
    """Gera um hash simples e consistente para senha usando scrypt."""

    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Valida uma senha em texto puro contra o hash salvo."""

    try:
        algorithm, salt_hex, digest_hex = stored_hash.split("$", maxsplit=2)
    except ValueError:
        return False

    if algorithm != "scrypt":
        return False

    expected = bytes.fromhex(digest_hex)
    candidate = hashlib.scrypt(
        password.encode("utf-8"),
        salt=bytes.fromhex(salt_hex),
        n=2**14,
        r=8,
        p=1,
    )
    return hmac.compare_digest(candidate, expected)


def hash_session_token(session_token: str) -> str:
    """Transforma o token bruto em hash para persistencia."""

    return hashlib.sha256(session_token.encode("utf-8")).hexdigest()


def build_identity(user: object) -> AuthenticatedIdentity:
    """Converte um usuario ORM em identidade autenticada simples."""

    return AuthenticatedIdentity(
        user_id=getattr(user, "id"),
        email=getattr(user, "email"),
        role=getattr(user, "role"),
        is_active=getattr(user, "is_active"),
        created_at=getattr(user, "created_at"),
    )


def login_with_email_and_password(email: str, password: str) -> LoginResult:
    """Autentica um usuario e cria uma sessao persistida."""

    normalized_email = email.strip().lower()
    user = get_user_by_email(normalized_email)
    if user is None or not getattr(user, "is_active") or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError("invalid_credentials")

    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=DEFAULT_AUTH_SESSION_TTL_HOURS)
    create_auth_session(
        user_id=user.id,
        session_token_hash=hash_session_token(session_token),
        expires_at=expires_at,
    )
    return LoginResult(
        session_token=session_token,
        expires_at=expires_at,
        identity=build_identity(user),
    )


def get_identity_from_session_token(session_token: str) -> AuthenticatedIdentity:
    """Resolve a identidade a partir de um token de sessao bruto."""

    token_hash = hash_session_token(session_token)
    auth_session = get_auth_session_by_token_hash(token_hash)
    if auth_session is None:
        raise InvalidSessionError("missing_session")
    if auth_session.revoked_at is not None:
        raise InvalidSessionError("revoked_session")
    if auth_session.expires_at <= datetime.utcnow():
        raise InvalidSessionError("expired_session")

    user = get_user_by_id(auth_session.user_id)
    if user is None or not getattr(user, "is_active"):
        raise InvalidSessionError("invalid_user")
    return build_identity(user)


def logout_session(session_token: str) -> None:
    """Revoga a sessao autenticada atual."""

    revoked = revoke_auth_session_by_token_hash(hash_session_token(session_token))
    if not revoked:
        raise InvalidSessionError("missing_session")
