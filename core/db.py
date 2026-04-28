from functools import lru_cache

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from core.config import get_settings
from core.models import Base


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
    """Cria as tabelas do banco e ajusta colunas novas quando necessario."""

    Base.metadata.create_all(bind=get_engine())
    _ensure_run_items_columns()


def ping_database() -> bool:
    """Executa uma consulta simples para validar conectividade com o banco."""

    with get_engine().connect() as connection:
        connection.execute(text("SELECT 1"))
    return True


def _ensure_run_items_columns() -> None:
    """Adiciona colunas novas em `run_items` quando o banco ja existia antes da feature."""

    engine = get_engine()
    inspector = inspect(engine)

    if "run_items" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("run_items")}
    pending_columns = {
        "session_id": "ALTER TABLE run_items ADD COLUMN session_id VARCHAR(64) NOT NULL DEFAULT ''",
        "user_id": "ALTER TABLE run_items ADD COLUMN user_id INTEGER NULL",
        "channel": "ALTER TABLE run_items ADD COLUMN channel VARCHAR(32) NOT NULL DEFAULT 'terminal'",
        "status": "ALTER TABLE run_items ADD COLUMN status VARCHAR(16) NOT NULL DEFAULT 'success'",
        "error_text": "ALTER TABLE run_items ADD COLUMN error_text TEXT NULL",
    }

    missing_statements = [
        statement
        for column_name, statement in pending_columns.items()
        if column_name not in existing_columns
    ]
    if not missing_statements:
        return

    with engine.begin() as connection:
        for statement in missing_statements:
            connection.execute(text(statement))
