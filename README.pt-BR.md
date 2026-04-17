[Change the README language / Troque o idioma do README: English](./README.md) | [Português (Brasil)](./README.pt-BR.md)

# Terminal Agent

Terminal Agent é um assistente de IA com foco em terminal, construído com LangChain, LangGraph, Typer, SQLAlchemy e Groq. O projeto foca em um fluxo de chat prático no qual o usuário conversa com um agente, o agente pode chamar tools de tarefas quando necessário, e a interação final é salva em um banco de dados.

## Funcionalidades

- Interface de chat no terminal
- Logs de execução em tempo real enquanto o agente está trabalhando
- Operações de tarefas baseadas em tools
- Armazenamento persistente dos resultados das conversas
- Configuração por ambiente usando `.env`
- Comando global de terminal: `terminal-agent`

## Stack Tecnológica

- Python 3.11+
- Typer
- LangChain
- LangGraph
- Groq
- SQLAlchemy
- Pydantic Settings
- PostgreSQL ou SQLite

## Instalação

1. Instale o projeto em modo editável:
   `py -m pip install -e .`
2. Copie `.env.example` para `.env`
3. Defina seus valores de ambiente, principalmente:
   - `DATABASE_URL`
   - `GROQ_API_KEY`
   - `MODEL_NAME`, se quiser sobrescrever o modelo padrão

## Executando o Projeto

Inicie a aplicação de terminal com:

`terminal-agent`

Dentro do terminal:

- use `/help` para mostrar os comandos locais
- use `/exit` para sair da aplicação

Você também pode rodar o módulo diretamente:

`py -m app.cli`

## Observações para Windows

Quando instalado, o projeto cria `terminal-agent.exe` dentro da pasta `Scripts` do Python.

Para descobrir essa pasta, execute:

`py -c "import sysconfig; print(sysconfig.get_path('scripts'))"`

Esse diretório precisa estar no `PATH` se você quiser que `terminal-agent` funcione em qualquer novo terminal do PowerShell, CMD ou VS Code.

## Estrutura do Projeto

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

## Fluxo Principal

1. O usuário envia uma mensagem no terminal
2. A CLI chama o fluxo de execução do agente
3. O agente decide se deve chamar tools
4. Os resultados das tools retornam em JSON estruturado para o modelo interpretar
5. A resposta final é exibida no terminal
6. O resultado final da interação é salvo no banco de dados

## Notas

- O agente é configurado para explicar os resultados das tools de forma natural em vez de mostrar JSON bruto
- O agente decide quando cada tool de tarefa deve ser chamada
- O terminal exibe logs internos para que você entenda o que o agente está fazendo
