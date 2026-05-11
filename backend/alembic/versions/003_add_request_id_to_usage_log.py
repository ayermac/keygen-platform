"""add request_id and idempotency constraint to activation_log

Revision ID: 003
Revises: 002
Create Date: 2026-05-11
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("activation_log", sa.Column("request_id", sa.String(128), nullable=True))
    op.create_index("ix_activation_log_request_id", "activation_log", ["request_id"])
    op.create_unique_constraint(
        "uq_log_idempotency",
        "activation_log",
        ["category_id", "key_id", "action", "request_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_log_idempotency", "activation_log", type_="unique")
    op.drop_index("ix_activation_log_request_id", table_name="activation_log")
    op.drop_column("activation_log", "request_id")
