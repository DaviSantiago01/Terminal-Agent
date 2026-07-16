from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# __file__ = apps/backend/core/config.py → core → backend → apps → project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Configurações da aplicação carregadas das variáveis de ambiente e do .env."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),
    )

    database_url: str = Field(alias="DATABASE_URL")
    app_env: str = Field(default="development", alias="APP_ENV")
    model_name: str = Field(default="llama-3.1-8b-instant", alias="MODEL_NAME")
    groq_api_key: SecretStr | None = Field(default=None, alias="GROQ_API_KEY")
    min_message_interval_seconds: float = Field(default=1.5, alias="MIN_MESSAGE_INTERVAL_SECONDS")
    super_admin_email: str | None = Field(default=None, alias="SUPER_ADMIN_EMAIL")
    super_admin_password: SecretStr | None = Field(default=None, alias="SUPER_ADMIN_PASSWORD")
    auth_cookie_secure: bool | None = Field(default=None, alias="AUTH_COOKIE_SECURE")
    cors_allowed_origins_raw: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="CORS_ALLOWED_ORIGINS",
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Garante que o projeto use PostgreSQL como banco oficial."""

        if not value.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL must use PostgreSQL with the psycopg driver.")
        return value

    @property
    def auth_cookie_secure_enabled(self) -> bool:
        """Define se o cookie de sessão precisa exigir HTTPS."""

        if self.auth_cookie_secure is not None:
            return self.auth_cookie_secure
        return self.app_env.strip().lower() == "production"

    @property
    def cors_allowed_origins(self) -> list[str]:
        """Normaliza a lista de origens permitidas para o frontend web."""

        return [
            origin.strip()
            for origin in self.cors_allowed_origins_raw.split(",")
            if origin.strip()
        ]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Carrega as configurações uma vez e reutiliza o resultado na aplicação."""

    return Settings()
