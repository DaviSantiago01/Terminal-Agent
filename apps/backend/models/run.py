from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.backend.models.base import Base


class RunItem(Base):
    """Armazena cada interacao persistida com contexto basico de sessao."""

    __tablename__ = "run_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[str] = mapped_column(String(64), index=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True, default="")
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    channel: Mapped[str] = mapped_column(String(32), index=True, default="terminal")
    status: Mapped[str] = mapped_column(String(16), index=True, default="success")
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_text: Mapped[str] = mapped_column(Text)
    output_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
