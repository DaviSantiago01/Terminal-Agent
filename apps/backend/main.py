from fastapi import FastAPI

from apps.backend.routes.auth import router as auth_router
from apps.backend.routes.health import router as health_router

app = FastAPI(
    title="Terminal Agent API",
    version="0.1.0",
    description="API base para health e autenticacao do produto web.",
)

app.include_router(health_router)
app.include_router(auth_router)
