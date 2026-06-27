"""create weekly report in app notifications

Revision ID: 202606180021
Revises: 202606180020
Create Date: 2026-06-18 00:21:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "202606180021"
down_revision: str | None = "202606180020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pro_weekly_report_in_app_notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_run_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["delivery_run_id"], ["pro_weekly_report_delivery_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["delivery_run_item_id"],
            ["pro_weekly_report_delivery_run_items.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["pro_weekly_report_snapshots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_pro_weekly_report_in_app_notifications_delivery_run_id",
        "pro_weekly_report_in_app_notifications",
        ["delivery_run_id"],
    )
    op.create_index(
        "ix_pro_weekly_report_in_app_notifications_delivery_run_item_id",
        "pro_weekly_report_in_app_notifications",
        ["delivery_run_item_id"],
    )
    op.create_index(
        "ix_pro_weekly_report_in_app_notifications_merchant_id",
        "pro_weekly_report_in_app_notifications",
        ["merchant_id"],
    )
    op.create_index(
        "ix_pro_weekly_report_in_app_notifications_snapshot_id",
        "pro_weekly_report_in_app_notifications",
        ["snapshot_id"],
    )
    op.create_index(
        "ix_pro_weekly_report_in_app_notifications_status",
        "pro_weekly_report_in_app_notifications",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_pro_weekly_report_in_app_notifications_status",
        table_name="pro_weekly_report_in_app_notifications",
    )
    op.drop_index(
        "ix_pro_weekly_report_in_app_notifications_snapshot_id",
        table_name="pro_weekly_report_in_app_notifications",
    )
    op.drop_index(
        "ix_pro_weekly_report_in_app_notifications_merchant_id",
        table_name="pro_weekly_report_in_app_notifications",
    )
    op.drop_index(
        "ix_pro_weekly_report_in_app_notifications_delivery_run_item_id",
        table_name="pro_weekly_report_in_app_notifications",
    )
    op.drop_index(
        "ix_pro_weekly_report_in_app_notifications_delivery_run_id",
        table_name="pro_weekly_report_in_app_notifications",
    )
    op.drop_table("pro_weekly_report_in_app_notifications")
