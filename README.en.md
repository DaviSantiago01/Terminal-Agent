[Change the README language / Troque o idioma do README: [Português (Brasil)](./README.md) | English](./README.en.md)

# Terminal Agent

Terminal Agent is a terminal-first AI assistant built for practical conversations, task-oriented tool usage, and persistent interaction history. The current product focuses on a simple CLI workflow where the user talks to an agent, sees live logs, and receives a final answer saved in the database.

## Quick View

- Surface: terminal CLI
- Current focus: stable assistant loop with tools and persistence
- Best entry for project docs: [`docs/en/CONTEXT.md`](./docs/en/CONTEXT.md)
- Best entry for product direction: [`docs/en/PRD.md`](./docs/en/PRD.md)

## Stack

- Python 3.11+: foundation for the application and CLI.
- Typer: structures terminal commands and the user interaction loop.
- Pydantic and pydantic-settings: load, validate, and centralize configuration from `.env`.
- LangChain and LangGraph: organize the agent, tool usage, and the execution flow between input, reasoning, and final response.
- Groq: model provider used by the agent.
- SQLAlchemy: ORM and database access layer for persisted tasks and run history.
- psycopg: driver used by SQLAlchemy to connect the app to PostgreSQL.
- PostgreSQL: official database used to store tasks, run history, and future application data.

## Installation

1. Install the project in editable mode:
   `py -m pip install -e .`
2. Copy `.env.example` to `.env`
3. Set your environment values, especially:
   - `DATABASE_URL`
   - `GROQ_API_KEY`
   - `MODEL_NAME` if you want to override the default model

The project uses only PostgreSQL. The default `DATABASE_URL` already points to a local PostgreSQL instance.

## Running The Project

Start the terminal app with:

`terminal-agent`

Inside the terminal:

- use `/help` to show local commands
- use `/exit` to leave the application

You can also run the module directly:

`py -m app.cli`

## Terminal Example

```text
>> create a task to study English every day
voce: create a task to study English every day
log: agent: usando modelo
log: modelo: chamando task_create(task_key='study-english', input_text='Study English every day', is_active=True)
log: task_create: {"status":"created", ...}
terminal agent: Criei a task "study-english" para estudar inglês todos os dias.
```

## Docs

- [Product direction](./docs/en/PRD.md)
- [Architecture](./docs/en/ARCH.md)
- [Features and roadmap](./docs/en/FEATURES.md)
- [Feature briefs](./docs/en/feature/README.md)
- [Current context](./docs/en/CONTEXT.md)
