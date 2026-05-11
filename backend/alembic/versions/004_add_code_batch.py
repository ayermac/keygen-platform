"""add code_batch table

Revision ID: 004
Revises: 003
Create Date: 2026-05-11
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "code_batch",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("batch_id", sa.String(50), unique=True, nullable=False),
        sa.Column("category_id", sa.BigInteger, sa.ForeignKey("category.id"), nullable=False),
        sa.Column("card_type_name", sa.String(50), nullable=True),
        sa.Column("count", sa.Integer, nullable=False),
        sa.Column("total_score", sa.Integer, nullable=False),
        sa.Column("creator", sa.String(100), nullable=True),
        sa.Column("remark", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_code_batch_category_id", "code_batch", ["category_id"])


def downgrade() -> None:
    op.drop_index("ix_code_batch_category_id", table_name="code_batch")
    op.drop_table("code_batch")
