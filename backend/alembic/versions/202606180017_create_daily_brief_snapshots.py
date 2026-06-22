"""create daily brief snapshots

Revision ID: 202606180017
Revises: 202606180016
Create Date: 2026-06-22 00:17:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "202606180017"
down_revision: str | None = "202606180016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pro_daily_brief_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("brief_date", sa.Date(), nullable=False),
        sa.Column("today_sales_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("today_reservation_count", sa.Integer(), nullable=False),
        sa.Column("today_picked_up_count", sa.Integer(), nullable=False),
        sa.Column("today_cancelled_count", sa.Integer(), nullable=False),
        sa.Column("saved_quantity_today", sa.Integer(), nullable=False),
        sa.Column("unresolved_alert_count", sa.Integer(), nullable=False),
        sa.Column("action_started_alert_count", sa.Integer(), nullable=False),
        sa.Column("high_severity_alert_count", sa.Integer(), nullable=False),
        sa.Column("recommendation_action_count", sa.Integer(), nullable=False),
        sa.Column("pos_last_sync_status", sa.String(length=40), nullable=True),
        sa.Column("pos_last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("csv_recent_import_count", sa.Integer(), nullable=False),
        sa.Column("csv_recent_failed_count", sa.Integer(), nullable=False),
        sa.Column("inventory_event_count_today", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("merchant_id", "brief_date", name="uq_pro_daily_brief_snapshot_merchant_date"),
    )
    op.create_index(op.f("ix_pro_daily_brief_snapshots_brief_date"), "pro_daily_brief_snapshots", ["brief_date"], unique=False)
    op.create_index(op.f("ix_pro_daily_brief_snapshots_merchant_id"), "pro_daily_brief_snapshots", ["merchant_id"], unique=False)
    op.create_index(op.f("ix_pro_daily_brief_snapshots_store_id"), "pro_daily_brief_snapshots", ["store_id"], unique=False)

    op.create_table(
        "pro_daily_brief_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_type", sa.String(length=80), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("action_label", sa.String(length=120), nullable=True),
        sa.Column("action_href", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["snapshot_id"], ["pro_daily_brief_snapshots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pro_daily_brief_tasks_priority"), "pro_daily_brief_tasks", ["priority"], unique=False)
    op.create_index(op.f("ix_pro_daily_brief_tasks_snapshot_id"), "pro_daily_brief_tasks", ["snapshot_id"], unique=False)
    op.create_index(op.f("ix_pro_daily_brief_tasks_task_type"), "pro_daily_brief_tasks", ["task_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_pro_daily_brief_tasks_task_type"), table_name="pro_daily_brief_tasks")
    op.drop_index(op.f("ix_pro_daily_brief_tasks_snapshot_id"), table_name="pro_daily_brief_tasks")
    op.drop_index(op.f("ix_pro_daily_brief_tasks_priority"), table_name="pro_daily_brief_tasks")
    op.drop_table("pro_daily_brief_tasks")
    op.drop_index(op.f("ix_pro_daily_brief_snapshots_store_id"), table_name="pro_daily_brief_snapshots")
    op.drop_index(op.f("ix_pro_daily_brief_snapshots_merchant_id"), table_name="pro_daily_brief_snapshots")
    op.drop_index(op.f("ix_pro_daily_brief_snapshots_brief_date"), table_name="pro_daily_brief_snapshots")
    op.drop_table("pro_daily_brief_snapshots")
