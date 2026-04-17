[Change the README language / Troque o idioma do README: English](./README.md) | [Português (Brasil)](./README.pt-BR.md)

# Terminal Agent

Terminal Agent is a terminal-first AI assistant built for practical conversations, task-oriented tool usage, and persistent interaction history. The current product focuses on a simple CLI workflow where the user talks to an agent, sees live logs, and receives a final answer saved in the database.

## Quick View

- Surface: terminal CLI
- Current focus: stable assistant loop with tools and persistence
- Best entry for project docs: [`docs/CONTEXT.md`](./docs/CONTEXT.md)
- Best entry for product direction: [`docs/PRD.md`](./docs/PRD.md)

## Stack

- Python 3.11+
- Typer
- LangChain and LangGraph
- Groq
- SQLAlchemy
- PostgreSQL or SQLite

## Installation

1. Install the project in editable mode:
   `py -m pip install -e .`
2. Copy `.env.example` to `.env`
3. Set your environment values, especially:
   - `DATABASE_URL`
   - `GROQ_API_KEY`
   - `MODEL_NAME` if you want to override the default model

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

- [Product direction](./docs/PRD.md)
- [Architecture](./docs/ARCH.md)
- [Features and roadmap](./docs/FEATURES.md)
- [Feature briefs](./docs/feature/README.md)
- [Current context](./docs/CONTEXT.md)
