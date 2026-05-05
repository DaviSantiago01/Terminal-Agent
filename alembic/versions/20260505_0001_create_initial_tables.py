"""create initial tables

Revision ID: 20260505_0001
Revises: None
Create Date: 2026-05-05 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260505_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_key", sa.String(length=64), nullable=False),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_tasks_task_key", "tasks", ["task_key"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_is_active", "users", ["is_active"], unique=False)
    op.create_index("ix_users_role", "users", ["role"], unique=False)

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"], unique=False)
    op.create_index("ix_auth_sessions_session_token_hash", "auth_sessions", ["session_token_hash"], unique=True)
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"], unique=False)

    op.create_table(
        "run_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.String(length=64), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("channel", sa.String(length=32), nullable=False, server_default="terminal"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="success"),
        sa.Column("error_text", sa.Text(), nullable=True),
        sa.Column("input_text", sa.Text(), nullable=False),
        sa.Column("output_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index("ix_run_items_channel", "run_items", ["channel"], unique=False)
    op.create_index("ix_run_items_session_id", "run_items", ["session_id"], unique=False)
    op.create_index("ix_run_items_status", "run_items", ["status"], unique=False)
    op.create_index("ix_run_items_task_id", "run_items", ["task_id"], unique=False)
    op.create_index("ix_run_items_user_id", "run_items", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_run_items_user_id", table_name="run_items")
    op.drop_index("ix_run_items_task_id", table_name="run_items")
    op.drop_index("ix_run_items_status", table_name="run_items")
    op.drop_index("ix_run_items_session_id", table_name="run_items")
    op.drop_index("ix_run_items_channel", table_name="run_items")
    op.drop_table("run_items")

    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_session_token_hash", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_expires_at", table_name="auth_sessions")
    op.drop_table("auth_sessions")

    op.drop_index("ix_users_role", table_name="users")
    op.drop_index("ix_users_is_active", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_tasks_task_key", table_name="tasks")
    op.drop_table("tasks")
