from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
import os

from apps.backend.routes.auth import router as auth_router
from apps.backend.routes.health import router as health_router
from core.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gatilhos de Inicializacao e Encerramento da API.
    
    Realiza o seeding do Super Admin no banco de dados durante a inicializacao,
    utilizando credenciais definidas nas variaveis de ambiente.
    """
    from apps.backend.services.auth_service import hash_password
    from core.crud.auth import create_user, get_user_by_email
    import logging

    init_db()

    super_email = os.environ.get("SUPER_ADMIN_EMAIL")
    super_pass = os.environ.get("SUPER_ADMIN_PASSWORD")
    
    if super_email and super_pass:
        existing = get_user_by_email(super_email)
        if not existing:
            try:
                hashed = hash_password(super_pass)
                create_user(email=super_email, password_hash=hashed, role="admin", is_active=True)
                logging.info(f"Conta de admin '{super_email}' semeada com sucesso!")
            except Exception as e:
                logging.error(f"Aviso: ignorado erro ao tentar criar semente de admin: {e}")

    yield

app = FastAPI(
    title="Terminal Agent API",
    version="0.1.0",
    description="API base para health e autenticacao do produto web.",
    lifespan=lifespan
)

app.include_router(health_router)
app.include_router(auth_router)


def run() -> None:
    """Executa a API localmente via comando instalado."""

    uvicorn.run("apps.backend.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    run()
