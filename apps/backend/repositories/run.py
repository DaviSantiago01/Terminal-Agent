from apps.backend.core.db import create_session
from apps.backend.models.run import RunItem


def save_result(
    task_id: str,
    session_id: str,
    channel: str,
    status: str,
    input_text: str,
    output_text: str,
    error_text: str | None = None,
    user_id: int | None = None,
) -> None:
    """Persiste o resultado final exibido no terminal com contexto da execucao."""

    session = create_session()
    try:
        session.add(
            RunItem(
                task_id=task_id,
                session_id=session_id,
                user_id=user_id,
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
