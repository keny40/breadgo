"""create pro health alerts

Revision ID: 202606180023
Revises: 202606180022
Create Date: 2026-06-18 00:23:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "202606180023"
down_revision: str | None = "202606180022"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pro_health_alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("source", sa.String(length=80), nullable=False),
        sa.Column("source_key", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("details_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["acknowledged_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resolved_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pro_health_alerts_severity", "pro_health_alerts", ["severity"])
    op.create_index("ix_pro_health_alerts_status", "pro_health_alerts", ["status"])
    op.create_index("ix_pro_health_alerts_source", "pro_health_alerts", ["source"])
    op.create_index("ix_pro_health_alerts_source_key", "pro_health_alerts", ["source_key"])
    op.create_index(
        "ix_pro_health_alerts_acknowledged_by_user_id",
        "pro_health_alerts",
        ["acknowledged_by_user_id"],
    )
    op.create_index("ix_pro_health_alerts_resolved_by_user_id", "pro_health_alerts", ["resolved_by_user_id"])


def downgrade() -> None:
    op.drop_index("ix_pro_health_alerts_resolved_by_user_id", table_name="pro_health_alerts")
    op.drop_index("ix_pro_health_alerts_acknowledged_by_user_id", table_name="pro_health_alerts")
    op.drop_index("ix_pro_health_alerts_source_key", table_name="pro_health_alerts")
    op.drop_index("ix_pro_health_alerts_source", table_name="pro_health_alerts")
    op.drop_index("ix_pro_health_alerts_status", table_name="pro_health_alerts")
    op.drop_index("ix_pro_health_alerts_severity", table_name="pro_health_alerts")
    op.drop_table("pro_health_alerts")
