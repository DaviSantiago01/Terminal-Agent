from __future__ import annotations

import re
import time

import typer
from rich.console import Console
from rich.panel import Panel
from rich import box

from app.agent import execute_agent
from app.config import get_settings
from app.db import init_db, save_result

cli = typer.Typer(add_completion=False, help="Chat de terminal do agente")
console = Console()


def _print_banner() -> None:
    """Renderiza o painel inicial mostrado quando a aplicação começa."""

    console.print(
        Panel(
            "[bold]Terminal Agent[/bold]\n"
            "Agente: Planner\n\n"
            "[dim]Chat de terminal para planejar tasks, revisar ideias e conversar com o agente.[/dim]\n"
            "[dim]Use /help para ver como usar o chat e conhecer o comando disponível.[/dim]",
            title="Terminal Agent",
            border_style="#d97706",
            box=box.ROUNDED,
        )
    )


def _print_help() -> None:
    """Mostra o pequeno conjunto de comandos locais com barra."""

    console.print(
        Panel.fit(
            "[bold]/help[/bold] - mostra esta ajuda\n"
            "[bold]/exit[/bold] - sai do chat",
            title="Ajuda",
            border_style="blue",
        )
    )


def _print_user_message(message: str) -> None:
    """Renderiza a mensagem do usuário no estilo visual do terminal."""

    console.print(f"[bold white]voce:[/bold white] [white]{message}[/white]")


def _normalize_user_message(message: str) -> str:
    """Limpa a mensagem do usuário removendo espaços excessivos e caracteres de controle simples."""

    # Mantém quebras de linha úteis, mas remove outros caracteres de controle invisíveis.
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", message)

    # Limpa espaços sobrando no começo e no fim de cada linha.
    lines = [line.strip() for line in sanitized.splitlines()]

    # Remove linhas vazias repetidas e normaliza blocos de texto.
    compact_lines: list[str] = []
    last_line_was_empty = False
    for line in lines:
        is_empty = line == ""
        if is_empty and last_line_was_empty:
            continue
        compact_lines.append(line)
        last_line_was_empty = is_empty

    return "\n".join(compact_lines).strip()


def _can_process_message(last_message_at: float | None, min_interval_seconds: float) -> tuple[bool, float]:
    """Verifica se já passou o intervalo mínimo entre duas mensagens do usuário."""

    if last_message_at is None:
        return True, 0.0

    elapsed = time.monotonic() - last_message_at
    remaining = min_interval_seconds - elapsed
    return remaining <= 0, max(0.0, remaining)


def _print_rate_limit_warning(remaining_seconds: float) -> None:
    """Mostra um aviso curto quando o usuário envia mensagens rápido demais."""

    console.print(
        f"[yellow]Espere {remaining_seconds:.1f}s antes de enviar outra mensagem.[/yellow]"
    )


def _handle_slash_command(command: str) -> bool:
    """Trata comandos locais que não precisam chamar o agente de IA."""

    normalized = command.strip().lower()
    if normalized in {"/exit", "/quit"}:
        return False
    if normalized == "/help":
        _print_help()
        return True

    console.print("[yellow]Comando desconhecido. Use /help.[/yellow]")
    return True


def _print_agent_response(output: str) -> None:
    """Renderiza a resposta final devolvida pelo agente."""

    console.print(f"[bold #d1d5db]terminal agent:[/bold #d1d5db] [#d1d5db]{output}[/#d1d5db]")


def _print_agent_log(message: str) -> None:
    """Renderiza logs internos para o usuário acompanhar os passos do agente."""

    console.print(f"[dim #9ca3af]log:[/dim #9ca3af] [#9ca3af]{message}[/#9ca3af]")


def run_chat() -> None:
    """Loop principal do terminal: lê entrada, executa o agente, salva e imprime."""

    settings = get_settings()
    init_db()
    _print_banner()
    last_message_at: float | None = None

    while True:
        try:
            raw_user_input = console.input("[dim #9ca3af]>>[/dim #9ca3af] ")
        except (EOFError, KeyboardInterrupt):
            console.print()
            break

        user_input = _normalize_user_message(raw_user_input)
        if not user_input:
            continue

        if user_input.startswith("/"):
            keep_running = _handle_slash_command(user_input)
            if not keep_running:
                break
            continue

        can_process, remaining_seconds = _can_process_message(
            last_message_at,
            settings.min_message_interval_seconds,
        )
        if not can_process:
            _print_rate_limit_warning(remaining_seconds)
            continue

        last_message_at = time.monotonic()
        _print_user_message(user_input)

        try:
            execution = execute_agent(user_input, log_callback=_print_agent_log)
            output = execution.output
        except Exception as exc:
            output = f"Erro ao executar o agente: {exc}"

        try:
            save_result("terminal", user_input, output)
        except Exception as exc:
            console.print(f"[yellow]Aviso: não foi possível salvar o resultado: {exc}[/yellow]")

        _print_agent_response(output)


@cli.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Ponto de entrada do Typer usado pelo módulo e pelo comando instalado."""

    if ctx.invoked_subcommand is None:
        run_chat()


if __name__ == "__main__":
    cli()
