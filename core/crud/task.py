from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from core.db import create_session
from core.models.task import TaskItem


class TaskAlreadyExistsError(Exception):
    """Erro usado quando uma task nova tenta reutilizar um task_key ja existente."""

    pass


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
