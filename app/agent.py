from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Callable
import warnings

warnings.filterwarnings(
    "ignore",
    message="Core Pydantic V1 functionality isn't compatible with Python 3.14 or greater.*",
    category=UserWarning,
    module=r"langchain_core\._api\.deprecation",
)

from langchain.agents import create_agent as create_langchain_agent
from langchain_groq import ChatGroq

from app.config import get_settings
from app.tools import TOOLS

LogCallback = Callable[[str], None]


@dataclass
class AgentExecution:
    """Objeto simples com a resposta final e os logs de uma execução."""

    output: str
    logs: list[str] = field(default_factory=list)


def _stringify_content(content: object) -> str:
    """Converte diferentes formatos de mensagem do LangChain em uma string simples."""

    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
            else:
                parts.append(str(item))
        return " ".join(part.strip() for part in parts if part).strip()
    return str(content).strip()


def _format_tool_args(arguments: dict[str, object]) -> str:
    """Formata os argumentos da tool de um jeito legível para os logs do terminal."""

    return ", ".join(f"{key}={value!r}" for key, value in arguments.items())


def _emit_log(logs: list[str], callback: LogCallback | None, message: str) -> None:
    """Salva um log localmente e, se existir callback, envia para o terminal."""

    logs.append(message)
    if callback is not None:
        callback(message)


def create_agent():
    """Monta o agente com modelo, tools e instruções principais."""

    settings = get_settings()
    if not settings.groq_api_key or not settings.groq_api_key.get_secret_value():
        raise ValueError("GROQ_API_KEY is missing. Set it in your .env file.")

    llm = ChatGroq(
        model=settings.model_name,
        api_key=settings.groq_api_key,
        temperature=0,
        max_retries=0,
        timeout=30,
    )

    system_prompt = (
        "Voce e um assistente de planejamento pessoal em portugues do Brasil. "
        "Voce decide quando faz sentido chamar task_list, task_get, task_create, task_update e task_delete. "
        "Chame ferramentas apenas quando isso realmente ajudar a resolver o pedido do usuario. "
        "As ferramentas retornam JSON estruturado com campos como status, task, items, count e task_key. "
        "Leia esse JSON e transforme o resultado em uma resposta natural para o usuario. "
        "Nunca responda com o JSON bruto, a menos que o usuario peca explicitamente. "
        "Nao atualize nem apague tasks sem pedido explicito. "
        "Em operacoes que modificam estado, faca apenas a alteracao necessaria e depois responda ao usuario. "
        "Se o usuario pedir para criar uma task sem informar task_key, gere um identificador curto e legivel. "
        "Se uma tool retornar status not_found ou already_exists, explique isso ao usuario com suas palavras. "
        "Nao invente tasks nem resultados de ferramentas. "
        "Se nao houver tasks, responda isso diretamente. "
        "Responda de forma curta, clara e pratica."
    )

    return create_langchain_agent(llm, TOOLS, system_prompt=system_prompt)


@lru_cache(maxsize=1)
def get_agent():
    """Mantém uma instância em cache para reutilizar o agente entre mensagens."""

    return create_agent()


def execute_agent(input_text: str, log_callback: LogCallback | None = None) -> AgentExecution:
    """Executa uma mensagem do usuário no agente e coleta os logs da execução."""

    logs: list[str] = []
    _emit_log(logs, log_callback, "agent: usando modelo")

    agent = get_agent()
    final_output = ""

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": input_text}]},
        config={"recursion_limit": 6},
        stream_mode="updates",
    ):
        if "model" in chunk:
            for message in chunk["model"].get("messages", []):
                tool_calls = getattr(message, "tool_calls", [])
                if tool_calls:
                    # Mostra quais tools o modelo decidiu chamar e com quais argumentos.
                    for tool_call in tool_calls:
                        args = tool_call.get("args", {})
                        _emit_log(
                            logs,
                            log_callback,
                            f"modelo: chamando {tool_call['name']}({_format_tool_args(args)})",
                        )
                    continue

                content = _stringify_content(getattr(message, "content", ""))
                if content:
                    final_output = content
                    _emit_log(logs, log_callback, "modelo: resposta final pronta")

        if "tools" in chunk:
            # Também mostra o resultado bruto retornado por cada tool.
            for message in chunk["tools"].get("messages", []):
                tool_name = getattr(message, "name", "tool")
                content = _stringify_content(getattr(message, "content", ""))
                _emit_log(logs, log_callback, f"{tool_name}: {content}")

    if not final_output:
        final_output = "Nao consegui concluir a resposta do agente."
        _emit_log(logs, log_callback, "modelo: resposta final ausente")

    return AgentExecution(output=final_output, logs=logs)


def run_agent(input_text: str) -> str:
    """Atalho para quando só a resposta final em texto é necessária."""

    return execute_agent(input_text).output
