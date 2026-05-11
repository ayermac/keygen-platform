"""add client_ip to audit_log

Revision ID: 002
Revises: 001
Create Date: 2026-05-11
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("audit_log", sa.Column("client_ip", sa.String(45), nullable=True))


def downgrade() -> None:
    op.drop_column("audit_log", "client_ip")
