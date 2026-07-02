"""add user status and merchant plan

Revision ID: 202606180025
Revises: 202606180024
Create Date: 2026-06-18 00:25:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "202606180025"
down_revision: str | None = "202606180024"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    user_status = postgresql.ENUM("ACTIVE", "SUSPENDED", "DEACTIVATED", name="user_status")
    user_status.create(bind, checkfirst=True)
    merchant_plan = postgresql.ENUM("FREE", "PRO", name="merchant_plan")
    merchant_plan.create(bind, checkfirst=True)

    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE merchant_status ADD VALUE IF NOT EXISTS 'DEACTIVATED'")

    op.add_column(
        "users",
        sa.Column(
            "status",
            postgresql.ENUM("ACTIVE", "SUSPENDED", "DEACTIVATED", name="user_status", create_type=False),
            nullable=False,
            server_default="ACTIVE",
        ),
    )
    op.add_column("users", sa.Column("status_reason", sa.String(length=500), nullable=True))
    op.add_column("merchants", sa.Column("status_reason", sa.Text(), nullable=True))
    op.add_column(
        "merchants",
        sa.Column(
            "plan",
            postgresql.ENUM("FREE", "PRO", name="merchant_plan", create_type=False),
            nullable=False,
            server_default="FREE",
        ),
    )
    op.alter_column("users", "status", server_default=None)
    op.alter_column("merchants", "plan", server_default=None)


def downgrade() -> None:
    op.drop_column("merchants", "plan")
    op.drop_column("merchants", "status_reason")
    op.drop_column("users", "status_reason")
    op.drop_column("users", "status")
    postgresql.ENUM(name="merchant_plan").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="user_status").drop(op.get_bind(), checkfirst=True)
