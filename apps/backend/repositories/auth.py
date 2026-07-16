from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from apps.backend.core.config import get_settings
from apps.backend.core.db import create_session
from apps.backend.models.auth import AuthSession, User


class UserAlreadyExistsError(Exception):
    """Erro usado quando um email tenta ser criado duas vezes."""

    pass


class UserRoleForbiddenError(Exception):
    """Erro usado quando tenta-se criar um admin que nao e o SUPER_ADMIN_EMAIL."""

    pass


def create_user(
    email: str,
    password_hash: str,
    role: str = "user",
    is_active: bool = True,
) -> User:
    """
    Escritor Oficial de Usuarios no Banco de Dados.

    Alem de inserir, ela contem a barreira absoluta de Seguranca ('Super Admin Limit'):
    Qualquer tentativa de criar usuario com role="admin" verificara se o e-mail
    bate milimetricamente com a variavel SUPER_ADMIN_EMAIL protegida no Servidor.

    Args:
        email (str): E-mail de cadastro
        password_hash (str): Senha JA criptografada com scrypt
        role (str, optional): Papeis do tipo ("user" ou "admin"). Padrão eh "user".
        is_active (bool, optional): Bloqueia/Libera o login na criacao.

    Returns:
        User: A linha de usuario que acabou de nascer no Banco de Dados.

    Raises:
        UserRoleForbiddenError: Se um e-mail aleatorio tentar roubar o trono de admin.
        UserAlreadyExistsError: Se o e-mail ja existe na base.
    """

    normalized_email = email.lower().strip()

    if role == "admin":
        super_admin = get_settings().super_admin_email
        if not super_admin or normalized_email != super_admin.lower().strip():
            raise UserRoleForbiddenError(f"Apenas {super_admin} pode ser admin.")

    session = create_session()
    try:
        user = User(
            email=normalized_email,
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
