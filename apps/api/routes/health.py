from fastapi import APIRouter

from app.db import ping_database

router = APIRouter(tags=["health"])


@router.get("/health")
def get_health() -> dict[str, object]:
    """Retorna o estado minimo da API e do banco."""

    return {
        "status": "ok",
        "database": "ok" if ping_database() else "error",
    }
