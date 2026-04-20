[Troque o idioma do README / Change the README language: [Português (Brasil)](./README.md) | [English](./README.en.md)]

# Terminal Agent

Terminal Agent é um assistente de IA com foco em terminal, criado para conversas práticas, uso de tools orientadas a tarefas e histórico persistente de interações. Hoje o produto está centrado em um fluxo simples de CLI no qual o usuário conversa com o agente, acompanha logs em tempo real e recebe uma resposta final salva no banco.

## Visão Rápida

- Superfície principal: terminal CLI
- Foco atual: loop do assistente estável com tools e persistência

## Stack

- Python 3.11+: base da aplicação e da CLI.
- Typer: estrutura os comandos de terminal e o ciclo de interação com o usuário.
- Pydantic e pydantic-settings: carregam, validam e centralizam as configurações vindas do `.env`.
- LangChain e LangGraph: organizam o agente, o uso de tools e o fluxo de execução entre entrada, raciocínio e resposta final.
- Groq: provedor do modelo de linguagem usado pelo agente.
- SQLAlchemy: camada ORM e de acesso ao banco para persistir tasks e execuções.
- psycopg: driver usado pelo SQLAlchemy para conectar a aplicação ao PostgreSQL.
- PostgreSQL: banco de dados oficial do projeto para salvar tasks, histórico de execuções e dados futuros da aplicação.

## Instalação

1. Instale o projeto em modo editável:
   `py -m pip install -e .`
2. Copie `.env.example` para `.env`
3. Defina os valores de ambiente, principalmente:
   - `DATABASE_URL`
   - `GROQ_API_KEY`
   - `MODEL_NAME`, se quiser trocar o modelo padrão

O projeto usa apenas PostgreSQL. O valor padrão atual de `DATABASE_URL` já aponta para uma instância PostgreSQL local.

## Como Rodar

Inicie a aplicação com:

`terminal-agent`

Dentro do terminal:

- use `/help` para mostrar os comandos locais
- use `/exit` para sair da aplicação

Você também pode rodar o módulo diretamente:

`py -m app.cli`

## Exemplo no Terminal

```text
>> criar uma task para estudar inglês todos os dias
voce: criar uma task para estudar inglês todos os dias
log: agent: usando modelo
log: modelo: chamando task_create(task_key='study-english', input_text='Study English every day', is_active=True)
log: task_create: {"status":"created", ...}
terminal agent: Criei a task "study-english" para estudar inglês todos os dias.
```
