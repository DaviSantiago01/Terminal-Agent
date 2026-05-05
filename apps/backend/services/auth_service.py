from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import hmac
import secrets

from core.crud.auth import (
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
    """
    Gera um "hash" (texto criptografado) para a senha do usuario.
    
    Como funciona:
    Usa o algoritmo 'scrypt', projetado para ser propositalmente lento. 
    Isso impede que hackers tentem adivinhar milhares de senhas por segundo.
    Adiciona um "salt" (tempero aleatorio) para garantir que duas senhas
    iguais nao gerem o mesmo resultado no banco.

    Args:
        password (str): A senha em texto puro digitada pelo usuario.

    Returns:
        str: A senha criptografada pronta para ser salva no banco.
    """

    # Cria 16 bytes aleatorios para baguncar a criptografia
    salt = secrets.token_bytes(16)
    
    # Executa o calculo matematico pesado
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1)
    
    # Junta tudo num formato padrao para salvarmos no banco
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Confere se a senha digitada esta correta.
    
    Como funciona:
    O sistema nunca descriptografa a senha salva. Em vez disso, ele
    pega a senha digitada agora, aplica a MESMA formula e "tempero" (salt),
    e v se o resultado bate com a string gravada no banco.

    Args:
        password (str): Senha digitada na tela de login.
        stored_hash (str): O hash bizarro inteiro salvo no banco de dados.

    Returns:
        bool: True se a senha confere, False se estiver errada.
    """

    try:
        # Separa as 3 partes que salvamos: algoritmo $ tempero $ resultado
        algorithm, salt_hex, digest_hex = stored_hash.split("$", maxsplit=2)
    except ValueError:
        return False

    if algorithm != "scrypt":
        return False

    expected = bytes.fromhex(digest_hex)
    
    # Pega a tentativa de senha e recalcula com o mesmo "tempero" (salt)
    candidate = hashlib.scrypt(
        password.encode("utf-8"),
        salt=bytes.fromhex(salt_hex),
        n=2**14,
        r=8,
        p=1,
    )
    
    # Compara de forma segura (previne descobrirem a senha pelo tempo de resposta)
    return hmac.compare_digest(candidate, expected)


def hash_session_token(session_token: str) -> str:
    """
    Camufla o token original antes de salvar no banco de dados.
    
    Aplica SHA-256 no token. Esse algoritmo e leve e rapido (diferente do scrypt para senhas).
    Protege o sistema: se o banco de dados vazar, o hacker vera apenas os hashes
    e nao conseguira montar o Cookie/Header para roubar as contas.

    Args:
        session_token (str): O token original gigante dado ao usuario.
    
    Returns:
        str: A string camuflada para compararmos no banco.
    """

    return hashlib.sha256(session_token.encode("utf-8")).hexdigest()


def build_identity(user: object) -> AuthenticatedIdentity:
    """
    Traduz o objeto do banco de dados (ORM) num formato simples de Identidade.
    Garante que senhas ou campos perigosos nao circulem pelos arquivos do sistema.
    """

    return AuthenticatedIdentity(
        user_id=getattr(user, "id"),
        email=getattr(user, "email"),
        role=getattr(user, "role"),
        is_active=getattr(user, "is_active"),
        created_at=getattr(user, "created_at"),
    )


def login_with_email_and_password(email: str, password: str) -> LoginResult:
    """
    O coracao do processo de Login (Stateful Auth).
    
    Como funciona:
    1. Acha o usuario pelo e-mail e confere se ativado.
    2. Compara a senha criptograficamente (verify_password).
    3. Gera a "Chave Aleatoria do Hotel" (Opaque Token).
    4. Salva apenas o fantasma da chave (hash) no banco com validade de 24h.
    
    Args:
        email (str): E-mail enviado na tela de login.
        password (str): Senha pura enviada na tela de login.

    Returns:
        LoginResult: Pacote contendo o token limpo (para devolver no Cookie) 
                     e os dados visuais do usuario (email, id, role).
    """

    # Limpa espacos vazios e letras maiusculas do email antes de buscar
    normalized_email = email.strip().lower()
    user = get_user_by_email(normalized_email)
    
    # Valida existencia, suspensao e finalmente checa a senha
    if user is None or not getattr(user, "is_active") or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError("invalid_credentials")

    # Gera 32 bytes garantidamente seguros contra adivinhacao matematicas
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=DEFAULT_AUTH_SESSION_TTL_HOURS)
    
    # Guarda registro no log do hotel (no banco de dados, via hash)
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
    """
    Traduz uma Chave de Sessao num Usuario confiavel da base de dados.
    
    Validacoes em sequencia:
    1. Calcula o (hash) do que recebeu e procura no banco.
    2. Se nao tem, rejeita.
    3. Se esta com "data de revogado", rejeita (baniu/deslogou).
    4. Se o tempo da sessao estourou as 24h, rejeita.
    5. Se o proprio dono da conta ta suspenso ("active=False"), rejeita o token dele.

    Args:
        session_token (str): O token cru, limpo, extraido do Cookie ou Header.
    """

    token_hash = hash_session_token(session_token)
    auth_session = get_auth_session_by_token_hash(token_hash)
    
    if auth_session is None:
        raise InvalidSessionError("missing_session")
    if auth_session.revoked_at is not None:
        raise InvalidSessionError("revoked_session")
    if auth_session.expires_at <= datetime.utcnow():
        raise InvalidSessionError("expired_session")

    # Confere se os super poderes ou ativacao do usuario mudaram!
    user = get_user_by_id(auth_session.user_id)
    if user is None or not getattr(user, "is_active"):
        raise InvalidSessionError("invalid_user")
        
    return build_identity(user)


def logout_session(session_token: str) -> None:
    """
    Mata um token instantaneamente marcando-o como revogado no banco de dados.
    Maneira agressiva de forcar Deslogar aparelhos em tempo real.
    """

    revoked = revoke_auth_session_by_token_hash(hash_session_token(session_token))
    if not revoked:
        raise InvalidSessionError("missing_session")
