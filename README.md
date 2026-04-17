[Change the README language / Troque o idioma do README: English](./README.md) | [Português (Brasil)](./README.pt-BR.md)

# Terminal Agent

Terminal Agent is a terminal-first AI assistant built with LangChain, LangGraph, Typer, SQLAlchemy, and Groq. The project focuses on a practical chat workflow where the user talks to an agent, the agent can call task tools when needed, and the final interaction is stored in a database.

## Documentation Model

- `docs/SDD.md` is the tracked technical source of truth for implementation behavior
- `docs/PRD.MD` is a private product-direction document kept local and ignored by Git
- Changes to behavior, interfaces, architecture, or constraints should update documentation before or together with code changes

## Features

- Terminal chat interface
- Live execution logs while the agent is working
- Tool-based task operations
- Persistent chat result storage
- Configurable environment through `.env`
- Global terminal command: `terminal-agent`

## Tech Stack

- Python 3.11+
- Typer
- LangChain
- LangGraph
- Groq
- SQLAlchemy
- Pydantic Settings
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

## Windows Notes

When installed, the project creates `terminal-agent.exe` inside your Python `Scripts` directory.

To discover that folder, run:

`py -c "import sysconfig; print(sysconfig.get_path('scripts'))"`

That directory must be in `PATH` if you want `terminal-agent` to work in any new PowerShell, CMD, or VS Code terminal.

## Project Structure

```text
app/
  agent.py
  cli.py
  config.py
  db.py
  tools.py
docs/
  PRD.MD
  SDD.md
README.md
README.pt-BR.md
pyproject.toml
```

## Technical Source Of Truth

If you are contributing to the implementation, read `docs/SDD.md` first. It defines the runtime flow, module responsibilities, tool contracts, persistence behavior, configuration model, and system constraints.

## Main Flow

1. The user sends a message in the terminal
2. The CLI calls the agent execution flow
3. The agent decides whether it should call tools
4. Tool results are returned in structured JSON for the model to interpret
5. The final response is printed in the terminal
6. The final interaction result is saved in the database

## Notes

- The agent is configured to explain tool results naturally instead of showing raw JSON
- The agent decides when each task tool should be called
- The terminal displays internal logs so you can understand what the agent is doing

## Contribution Workflow

1. Review `docs/SDD.md` before changing core behavior
2. Update `docs/SDD.md` when behavior, interfaces, architecture, persistence rules, or configuration rules change
3. Keep code comments and docstrings in Portuguese
4. Keep public project documentation in English
