from apps.backend.core.db import init_db


def run() -> None:
    """Executa as migrations do banco de dados sob demanda."""

    init_db()


if __name__ == "__main__":
    run()
