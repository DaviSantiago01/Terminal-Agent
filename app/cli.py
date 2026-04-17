from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich import box

from app.agent import execute_agent
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

    init_db()
    _print_banner()

    while True:
        try:
            user_input = console.input("[dim #9ca3af]>>[/dim #9ca3af] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            keep_running = _handle_slash_command(user_input)
            if not keep_running:
                break
            continue

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
