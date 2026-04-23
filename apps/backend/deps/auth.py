from fastapi import Header, HTTPException, status

from apps.backend.services.auth_service import InvalidSessionError, get_identity_from_session_token


def extract_bearer_token(authorization: str | None) -> str:
    """Extrai o token bearer do header Authorization."""

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing_authorization",
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_authorization_scheme",
        )
    return token.strip()


def get_current_identity(authorization: str | None = Header(default=None)):
    """Retorna a identidade autenticada a partir do token de sessao."""

    token = extract_bearer_token(authorization)
    try:
        return get_identity_from_session_token(token)
    except InvalidSessionError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
