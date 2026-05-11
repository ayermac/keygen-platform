"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-11
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- admin_user ---
    op.create_table(
        "admin_user",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(50), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # --- category (Product) ---
    op.create_table(
        "category",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(50), unique=True, nullable=False),
        sa.Column("score_per_key", sa.Integer, nullable=False),
        sa.Column("score_label", sa.String(50), nullable=False, server_default="积分"),
        sa.Column("max_activations", sa.Integer, nullable=False, server_default="1"),
        sa.Column("expiry_days", sa.Integer, nullable=True),
        sa.Column("api_key", sa.String(80), unique=True, nullable=False),
        sa.Column("card_types", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # --- activation_key (RedemptionCode) ---
    op.create_table(
        "activation_key",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("key_code", sa.String(19), unique=True, nullable=False),
        sa.Column("category_id", sa.BigInteger, sa.ForeignKey("category.id"), nullable=False),
        sa.Column(
            "status",
            sa.Enum("unused", "activated", "expired", "disabled", name="key_status"),
            nullable=False,
            server_default="unused",
        ),
        sa.Column("batch_id", sa.String(50), nullable=True),
        sa.Column("card_type_name", sa.String(50), nullable=True),
        sa.Column("total_score", sa.Integer, nullable=False),
        sa.Column("remaining_score", sa.Integer, nullable=False),
        sa.Column("expiry_days", sa.Integer, nullable=True),
        sa.Column("activated_at", sa.DateTime, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("metadata", sa.JSON, nullable=True),
    )
    op.create_index("ix_activation_key_category_id", "activation_key", ["category_id"])
    op.create_index("ix_activation_key_batch_id", "activation_key", ["batch_id"])

    # --- activation_log (UsageLog) ---
    op.create_table(
        "activation_log",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("key_id", sa.BigInteger, sa.ForeignKey("activation_key.id"), nullable=False),
        sa.Column("category_id", sa.BigInteger, sa.ForeignKey("category.id"), nullable=False),
        sa.Column(
            "action",
            sa.Enum("activate", "deduct", name="log_action"),
            nullable=False,
        ),
        sa.Column("amount", sa.Integer, nullable=False),
        sa.Column("remaining_after", sa.Integer, nullable=False),
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column("client_ip", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_activation_log_key_id", "activation_log", ["key_id"])
    op.create_index("ix_activation_log_category_id", "activation_log", ["category_id"])

    # --- audit_log ---
    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column("admin_id", sa.BigInteger, sa.ForeignKey("admin_user.id"), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("target_id", sa.BigInteger, nullable=True),
        sa.Column("detail", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_log_admin_id", "audit_log", ["admin_id"])


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("activation_log")
    op.drop_table("activation_key")
    op.drop_table("category")
    op.drop_table("admin_user")
    op.execute("DROP TYPE IF EXISTS key_status")
    op.execute("DROP TYPE IF EXISTS log_action")
