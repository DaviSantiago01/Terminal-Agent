from __future__ import annotations

import json
import warnings

warnings.filterwarnings(
    "ignore",
    message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.*",
    category=UserWarning,
    module=r"langchain_core\._api\.deprecation",
)

from langchain_core.tools import tool

from app.db import (
    TaskAlreadyExistsError,
    create_task as create_task_record,
    delete_task as delete_task_record,
    get_task_by_key as get_task_record_by_key,
    list_tasks as list_task_records,
    update_task as update_task_record,
)


def _serialize_task(task: object) -> dict[str, object]:
    """Converte um objeto de task do banco em dados simples compatíveis com JSON."""

    return {
        "task_key": getattr(task, "task_key"),
        "input_text": getattr(task, "input_text"),
        "is_active": getattr(task, "is_active"),
        "created_at": getattr(task, "created_at").isoformat(),
    }


@tool("task_list")
def task_list(active_only: bool = False) -> str:
    """Lista tasks e retorna JSON estruturado para o agente interpretar."""

    # O modelo vai ler este JSON e decidir como explicar o resultado ao usuário.
    tasks = list_task_records(active_only=active_only)
    return json.dumps(
        {
            "status": "ok",
            "active_only": active_only,
            "count": len(tasks),
            "items": [_serialize_task(task) for task in tasks],
        },
        ensure_ascii=False,
    )


@tool("task_get")
def task_get(task_key: str) -> str:
    """Busca uma task pelo identificador e retorna JSON estruturado."""

    task = get_task_record_by_key(task_key)
    if task is None:
        return json.dumps({"status": "not_found", "task_key": task_key}, ensure_ascii=False)
    return json.dumps({"status": "ok", "task": _serialize_task(task)}, ensure_ascii=False)


@tool("task_create")
def task_create(task_key: str, input_text: str, is_active: bool = True) -> str:
    """Cria uma task e retorna JSON estruturado."""

    try:
        task = create_task_record(task_key=task_key, input_text=input_text, is_active=is_active)
    except TaskAlreadyExistsError:
        return json.dumps({"status": "already_exists", "task_key": task_key}, ensure_ascii=False)
    return json.dumps({"status": "created", "task": _serialize_task(task)}, ensure_ascii=False)


@tool("task_update")
def task_update(task_key: str, input_text: str | None = None, is_active: bool | None = None) -> str:
    """Atualiza uma task e retorna JSON estruturado."""

    task = update_task_record(task_key=task_key, input_text=input_text, is_active=is_active)
    if task is None:
        return json.dumps({"status": "not_found", "task_key": task_key}, ensure_ascii=False)
    return json.dumps({"status": "updated", "task": _serialize_task(task)}, ensure_ascii=False)


@tool("task_delete")
def task_delete(task_key: str) -> str:
    """Remove uma task e retorna JSON estruturado."""

    deleted = delete_task_record(task_key)
    if not deleted:
        return json.dumps({"status": "not_found", "task_key": task_key}, ensure_ascii=False)
    return json.dumps({"status": "deleted", "task_key": task_key}, ensure_ascii=False)


tasks_list = task_list

TOOLS = [task_list, task_get, task_create, task_update, task_delete]
