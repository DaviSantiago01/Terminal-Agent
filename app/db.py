from datetime import datetime
from functools import lru_cache

from sqlalchemy import DateTime, Integer, String, Text, create_engine, inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Classe base do SQLAlchemy usada por todos os modelos ORM do projeto."""

    pass


class TaskAlreadyExistsError(Exception):
    """Erro usado quando uma task nova tenta reutilizar um task_key ja existente."""

    pass


class RunItem(Base):
    """Armazena cada interacao persistida com contexto basico de sessao."""

    __tablename__ = "run_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[str] = mapped_column(String(64), index=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True, default="")
    channel: Mapped[str] = mapped_column(String(32), index=True, default="terminal")
    status: Mapped[str] = mapped_column(String(16), index=True, default="success")
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_text: Mapped[str] = mapped_column(Text)
    output_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TaskItem(Base):
    """Representa uma task salva no banco de dados."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    input_text: Mapped[str] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


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


def _ensure_run_items_columns() -> None:
    """Adiciona colunas novas em `run_items` quando o banco ja existia antes da feature."""

    engine = get_engine()
    inspector = inspect(engine)

    if "run_items" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("run_items")}
    pending_columns = {
        "session_id": "ALTER TABLE run_items ADD COLUMN session_id VARCHAR(64) NOT NULL DEFAULT ''",
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


def create_task(task_key: str, input_text: str, is_active: bool = True) -> TaskItem:
    """Insere uma nova task e devolve o objeto salvo."""

    session = create_session()
    try:
        task = TaskItem(task_key=task_key, input_text=input_text, is_active=is_active)
        session.add(task)
        session.commit()
        session.refresh(task)
        return task
    except IntegrityError as exc:
        session.rollback()
        raise TaskAlreadyExistsError(task_key) from exc
    finally:
        session.close()


def list_tasks(active_only: bool = False) -> list[TaskItem]:
    """Retorna as tasks ordenadas pela data de criacao."""

    session = create_session()
    try:
        statement = select(TaskItem).order_by(TaskItem.created_at.asc())
        if active_only:
            statement = statement.where(TaskItem.is_active.is_(True))
        return list(session.scalars(statement).all())
    finally:
        session.close()


def get_task_by_key(task_key: str) -> TaskItem | None:
    """Busca uma task pela sua chave unica."""

    session = create_session()
    try:
        statement = select(TaskItem).where(TaskItem.task_key == task_key)
        return session.scalars(statement).first()
    finally:
        session.close()


def update_task(task_key: str, input_text: str | None = None, is_active: bool | None = None) -> TaskItem | None:
    """Atualiza uma task e devolve o objeto atualizado, ou None se nao existir."""

    session = create_session()
    try:
        task = session.scalars(select(TaskItem).where(TaskItem.task_key == task_key)).first()
        if task is None:
            return None
        if input_text is not None:
            task.input_text = input_text
        if is_active is not None:
            task.is_active = is_active
        session.commit()
        session.refresh(task)
        return task
    finally:
        session.close()


def delete_task(task_key: str) -> bool:
    """Remove uma task pela chave e informa se alguma linha foi apagada."""

    session = create_session()
    try:
        task = session.scalars(select(TaskItem).where(TaskItem.task_key == task_key)).first()
        if task is None:
            return False
        session.delete(task)
        session.commit()
        return True
    finally:
        session.close()


def save_result(
    task_id: str,
    session_id: str,
    channel: str,
    status: str,
    input_text: str,
    output_text: str,
    error_text: str | None = None,
) -> None:
    """Persiste o resultado final exibido no terminal com contexto da execucao."""

    session = create_session()
    try:
        session.add(
            RunItem(
                task_id=task_id,
                session_id=session_id,
                channel=channel,
                status=status,
                error_text=error_text,
                input_text=input_text,
                output_text=output_text,
            )
        )
        session.commit()
    finally:
        session.close()
