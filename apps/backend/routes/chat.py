from uuid import uuid4

from fastapi import APIRouter, Depends

from apps.backend.deps.auth import get_current_identity
from apps.backend.core.agent import execute_agent
from apps.backend.repositories.run import save_result
from apps.backend.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def post_chat(
    payload: ChatRequest,
    identity=Depends(get_current_identity),
) -> ChatResponse:
    """Executa o agente autenticado e persiste o resultado da interação web."""

    message = payload.message.strip()
    session_id = payload.session_id or uuid4().hex

    if not message:
        return ChatResponse(output="Envie uma mensagem antes de continuar.", session_id=session_id)

    status = "success"
    error_text: str | None = None

    try:
        execution = execute_agent(message)
        output = execution.output
    except Exception as exc:
        status = "error"
        error_text = str(exc)
        output = f"Erro ao executar o agente: {exc}"

    save_result(
        task_id="web-chat",
        session_id=session_id,
        user_id=identity.user_id,
        channel="web",
        status=status,
        input_text=message,
        output_text=output,
        error_text=error_text,
    )

    return ChatResponse(output=output, session_id=session_id)
