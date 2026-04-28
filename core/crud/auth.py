from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from core.db import create_session
from core.models.auth import AuthSession, User


class UserAlreadyExistsError(Exception):
    """Erro usado quando um email tenta ser criado duas vezes."""

    pass


def create_user(
    email: str,
    password_hash: str,
    role: str = "user",
    is_active: bool = True,
) -> User:
    """Cria um usuario autenticavel."""

    session = create_session()
    try:
        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except IntegrityError as exc:
        session.rollback()
        raise UserAlreadyExistsError(email) from exc
    finally:
        session.close()


def get_user_by_email(email: str) -> User | None:
    """Busca um usuario pelo email."""

    session = create_session()
    try:
        statement = select(User).where(User.email == email)
        return session.scalars(statement).first()
    finally:
        session.close()


def get_user_by_id(user_id: int) -> User | None:
    """Busca um usuario pelo identificador."""

    session = create_session()
    try:
        statement = select(User).where(User.id == user_id)
        return session.scalars(statement).first()
    finally:
        session.close()


def create_auth_session(user_id: int, session_token_hash: str, expires_at: datetime) -> AuthSession:
    """Cria uma sessao autenticada persistida."""

    session = create_session()
    try:
        auth_session = AuthSession(
            user_id=user_id,
            session_token_hash=session_token_hash,
            expires_at=expires_at,
        )
        session.add(auth_session)
        session.commit()
        session.refresh(auth_session)
        return auth_session
    finally:
        session.close()


def get_auth_session_by_token_hash(session_token_hash: str) -> AuthSession | None:
    """Busca uma sessao autenticada pelo hash do token."""

    session = create_session()
    try:
        statement = select(AuthSession).where(AuthSession.session_token_hash == session_token_hash)
        return session.scalars(statement).first()
    finally:
        session.close()


def revoke_auth_session_by_token_hash(session_token_hash: str) -> bool:
    """Revoga a sessao atual caso ela exista."""

    session = create_session()
    try:
        auth_session = session.scalars(
            select(AuthSession).where(AuthSession.session_token_hash == session_token_hash)
        ).first()
        if auth_session is None or auth_session.revoked_at is not None:
            return False
        auth_session.revoked_at = datetime.utcnow()
        session.commit()
        return True
    finally:
        session.close()
