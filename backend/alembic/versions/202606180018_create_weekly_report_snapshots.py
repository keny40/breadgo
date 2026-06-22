"""create weekly report snapshots

Revision ID: 202606180018
Revises: 202606180017
Create Date: 2026-06-22 00:18:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "202606180018"
down_revision: str | None = "202606180017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pro_weekly_report_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("total_sales_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_reservation_count", sa.Integer(), nullable=False),
        sa.Column("total_picked_up_count", sa.Integer(), nullable=False),
        sa.Column("total_cancelled_count", sa.Integer(), nullable=False),
        sa.Column("total_saved_quantity", sa.Integer(), nullable=False),
        sa.Column("average_unresolved_alert_count", sa.Numeric(8, 2), nullable=False),
        sa.Column("high_severity_alert_count", sa.Integer(), nullable=False),
        sa.Column("total_recommendation_action_count", sa.Integer(), nullable=False),
        sa.Column("total_inventory_event_count", sa.Integer(), nullable=False),
        sa.Column("pos_sync_issue_count", sa.Integer(), nullable=False),
        sa.Column("csv_import_error_count", sa.Integer(), nullable=False),
        sa.Column("text_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("merchant_id", "start_date", "end_date", name="uq_pro_weekly_report_snapshot_period"),
    )
    op.create_index(op.f("ix_pro_weekly_report_snapshots_end_date"), "pro_weekly_report_snapshots", ["end_date"], unique=False)
    op.create_index(op.f("ix_pro_weekly_report_snapshots_merchant_id"), "pro_weekly_report_snapshots", ["merchant_id"], unique=False)
    op.create_index(op.f("ix_pro_weekly_report_snapshots_start_date"), "pro_weekly_report_snapshots", ["start_date"], unique=False)
    op.create_index(op.f("ix_pro_weekly_report_snapshots_store_id"), "pro_weekly_report_snapshots", ["store_id"], unique=False)

    op.create_table(
        "pro_weekly_report_insights",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["snapshot_id"], ["pro_weekly_report_snapshots.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pro_weekly_report_insights_snapshot_id"), "pro_weekly_report_insights", ["snapshot_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_pro_weekly_report_insights_snapshot_id"), table_name="pro_weekly_report_insights")
    op.drop_table("pro_weekly_report_insights")
    op.drop_index(op.f("ix_pro_weekly_report_snapshots_store_id"), table_name="pro_weekly_report_snapshots")
    op.drop_index(op.f("ix_pro_weekly_report_snapshots_start_date"), table_name="pro_weekly_report_snapshots")
    op.drop_index(op.f("ix_pro_weekly_report_snapshots_merchant_id"), table_name="pro_weekly_report_snapshots")
    op.drop_index(op.f("ix_pro_weekly_report_snapshots_end_date"), table_name="pro_weekly_report_snapshots")
    op.drop_table("pro_weekly_report_snapshots")
