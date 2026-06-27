"""create pro operations audit logs

Revision ID: 202606180022
Revises: 202606180021
Create Date: 2026-06-18 00:22:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "202606180022"
down_revision: str | None = "202606180021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pro_operations_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_role", sa.String(length=40), nullable=False),
        sa.Column("action_type", sa.String(length=80), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pro_operations_audit_logs_actor_user_id", "pro_operations_audit_logs", ["actor_user_id"])
    op.create_index("ix_pro_operations_audit_logs_actor_role", "pro_operations_audit_logs", ["actor_role"])
    op.create_index("ix_pro_operations_audit_logs_action_type", "pro_operations_audit_logs", ["action_type"])
    op.create_index("ix_pro_operations_audit_logs_target_type", "pro_operations_audit_logs", ["target_type"])
    op.create_index("ix_pro_operations_audit_logs_target_id", "pro_operations_audit_logs", ["target_id"])
    op.create_index("ix_pro_operations_audit_logs_status", "pro_operations_audit_logs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_pro_operations_audit_logs_status", table_name="pro_operations_audit_logs")
    op.drop_index("ix_pro_operations_audit_logs_target_id", table_name="pro_operations_audit_logs")
    op.drop_index("ix_pro_operations_audit_logs_target_type", table_name="pro_operations_audit_logs")
    op.drop_index("ix_pro_operations_audit_logs_action_type", table_name="pro_operations_audit_logs")
    op.drop_index("ix_pro_operations_audit_logs_actor_role", table_name="pro_operations_audit_logs")
    op.drop_index("ix_pro_operations_audit_logs_actor_user_id", table_name="pro_operations_audit_logs")
    op.drop_table("pro_operations_audit_logs")
