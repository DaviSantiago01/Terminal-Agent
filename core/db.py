from functools import lru_cache
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from core.config import get_settings


@lru_cache(maxsize=1)
def get_engine():
    """Cria o engine do banco apenas uma vez, na primeira vez que ele for necessario."""

    settings = get_settings()
    return create_engine(settings.database_url, future=True)


@lru_cache(maxsize=1)
def get_session_factory():
    """Cria e mantem em cache a fabrica de sessoes do SQLAlchemy."""

    return sessionmaker(bind=get_engine(), class_=Session, autoflush=False, autocommit=False)


def create_session() -> Session:
    """Abre uma sessao de banco para uma operacao especifica."""

    return get_session_factory()()


def init_db() -> None:
    """Aplica as migrations do Alembic ate a versao mais recente."""

    command.upgrade(_get_alembic_config(), "head")


def ping_database() -> bool:
    """Executa uma consulta simples para validar conectividade com o banco."""

    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
    return True


def _get_alembic_config() -> Config:
    """Monta a configuracao do Alembic apontando para os arquivos do repositorio."""

    base_dir = Path(__file__).resolve().parent.parent
    config = Config(str(base_dir / "alembic.ini"))
    config.set_main_option("script_location", str(base_dir / "alembic"))
    config.set_main_option("sqlalchemy.url", get_settings().database_url)
    return config
