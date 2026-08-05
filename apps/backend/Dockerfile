FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md README.en.md alembic.ini ./
COPY apps/backend ./apps/backend

RUN pip install --no-cache-dir .

EXPOSE 8000
