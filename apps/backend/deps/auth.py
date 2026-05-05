from fastapi import Cookie, HTTPException, status

from apps.backend.services.auth_service import InvalidSessionError, get_identity_from_session_token


def get_current_identity(session_token: str | None = Cookie(default=None)):
    """
    Guarda-costas do sistema. Valida quem e o usuario antes de liberar o acesso a rota.

    Estrategia de Busca:
    1. Le o cookie `session_token` enviado automaticamente pelo navegador.
    2. Valida no banco de dados se a sessao nao expirou ou foi revogada.

    Args:
        session_token (str): Capturado automaticamente pelo FastAPI dos Cookies HttpOnly.

    Returns:
        AuthenticatedIdentity: Um objeto contendo id, email e permissoes do usuario.

    Raises:
        HTTPException: Erro 401 caso o cookie nao exista, esteja vencido ou seja invalido.
    """

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_session_context",
        )

    try:
        return get_identity_from_session_token(session_token)
    except InvalidSessionError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
