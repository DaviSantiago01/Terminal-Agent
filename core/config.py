from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Configurações da aplicação carregadas das variáveis de ambiente e do .env."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(alias="DATABASE_URL")
    model_name: str = Field(default="llama-3.1-8b-instant", alias="MODEL_NAME")
    groq_api_key: SecretStr | None = Field(default=None, alias="GROQ_API_KEY")
    min_message_interval_seconds: float = Field(default=1.5, alias="MIN_MESSAGE_INTERVAL_SECONDS")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Garante que o projeto use PostgreSQL como banco oficial."""

        if not value.startswith("postgresql+psycopg://"):
            raise ValueError("DATABASE_URL must use PostgreSQL with the psycopg driver.")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Carrega as configurações uma vez e reutiliza o resultado na aplicação."""

    return Settings()
