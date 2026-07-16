from fastapi import APIRouter, Depends, Cookie, Response, HTTPException, status

from apps.backend.core.config import get_settings
from apps.backend.deps.auth import get_current_identity
from apps.backend.schemas.auth import (
    AuthMeResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RegisterRequest,
    UserResponse,
)
from apps.backend.services.auth_service import (
    InvalidCredentialsError,
    InvalidSessionError,
    login_with_email_and_password,
    logout_session,
    register_with_email_and_password,
    UserAlreadyExistsServiceError,
    DEFAULT_AUTH_SESSION_TTL_HOURS,
)

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=LoginResponse)
def post_login(payload: LoginRequest, response: Response) -> LoginResponse:
    """Autentica um usuario por email e senha."""

    try:
        result = login_with_email_and_password(payload.email, payload.password)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid_credentials",
        ) from exc

    max_age_seconds = DEFAULT_AUTH_SESSION_TTL_HOURS * 3600
    response.set_cookie(
        key="session_token",
        value=result.session_token,
        max_age=max_age_seconds,
        httponly=True,
        samesite="lax",
        secure=settings.auth_cookie_secure_enabled,
    )

    return LoginResponse(
        expires_at=result.expires_at,
        user=UserResponse(
            id=result.identity.user_id,
            email=result.identity.email,
            role=result.identity.role,
            is_active=result.identity.is_active,
            created_at=result.identity.created_at,
        ),
    )


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def post_register(payload: RegisterRequest, response: Response) -> LoginResponse:
    """Cadastra um usuario comum e inicia a sessao autenticada imediatamente."""

    try:
        result = register_with_email_and_password(payload.email, payload.password)
    except UserAlreadyExistsServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="user_already_exists",
        ) from exc

    max_age_seconds = DEFAULT_AUTH_SESSION_TTL_HOURS * 3600
    response.set_cookie(
        key="session_token",
        value=result.session_token,
        max_age=max_age_seconds,
        httponly=True,
        samesite="lax",
        secure=settings.auth_cookie_secure_enabled,
    )

    return LoginResponse(
        expires_at=result.expires_at,
        user=UserResponse(
            id=result.identity.user_id,
            email=result.identity.email,
            role=result.identity.role,
            is_active=result.identity.is_active,
            created_at=result.identity.created_at,
        ),
    )


@router.post("/logout", response_model=LogoutResponse)
def post_logout(
    response: Response,
    session_token: str | None = Cookie(default=None),
) -> LogoutResponse:
    """Revoga a sessao autenticada atual e deleta o cookie."""

    if session_token:
        try:
            logout_session(session_token)
        except InvalidSessionError:
            pass

    response.delete_cookie(
        "session_token",
        httponly=True,
        samesite="lax",
        secure=settings.auth_cookie_secure_enabled,
    )
    return LogoutResponse(status="logged_out")


@router.get("/me", response_model=AuthMeResponse)
def get_me(identity=Depends(get_current_identity)) -> AuthMeResponse:
    """Retorna a identidade autenticada basica."""

    return AuthMeResponse(
        user=UserResponse(
            id=identity.user_id,
            email=identity.email,
            role=identity.role,
            is_active=identity.is_active,
            created_at=identity.created_at,
        )
    )
