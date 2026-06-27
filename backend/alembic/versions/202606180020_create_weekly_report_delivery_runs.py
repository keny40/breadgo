"""create weekly report delivery runs

Revision ID: 202606180020
Revises: 202606180019
Create Date: 2026-06-27 00:20:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "202606180020"
down_revision: str | None = "202606180019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pro_weekly_report_delivery_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_type", sa.String(length=40), nullable=False),
        sa.Column("channel", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("total_count", sa.Integer(), nullable=False),
        sa.Column("ready_count", sa.Integer(), nullable=False),
        sa.Column("skipped_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pro_weekly_report_delivery_runs_period_start"),
        "pro_weekly_report_delivery_runs",
        ["period_start"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pro_weekly_report_delivery_runs_period_end"),
        "pro_weekly_report_delivery_runs",
        ["period_end"],
        unique=False,
    )

    op.create_table(
        "pro_weekly_report_delivery_run_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["delivery_run_id"], ["pro_weekly_report_delivery_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["pro_weekly_report_snapshots.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pro_weekly_report_delivery_run_items_delivery_run_id"),
        "pro_weekly_report_delivery_run_items",
        ["delivery_run_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pro_weekly_report_delivery_run_items_merchant_id"),
        "pro_weekly_report_delivery_run_items",
        ["merchant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pro_weekly_report_delivery_run_items_snapshot_id"),
        "pro_weekly_report_delivery_run_items",
        ["snapshot_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_pro_weekly_report_delivery_run_items_snapshot_id"),
        table_name="pro_weekly_report_delivery_run_items",
    )
    op.drop_index(
        op.f("ix_pro_weekly_report_delivery_run_items_merchant_id"),
        table_name="pro_weekly_report_delivery_run_items",
    )
    op.drop_index(
        op.f("ix_pro_weekly_report_delivery_run_items_delivery_run_id"),
        table_name="pro_weekly_report_delivery_run_items",
    )
    op.drop_table("pro_weekly_report_delivery_run_items")
    op.drop_index(
        op.f("ix_pro_weekly_report_delivery_runs_period_end"),
        table_name="pro_weekly_report_delivery_runs",
    )
    op.drop_index(
        op.f("ix_pro_weekly_report_delivery_runs_period_start"),
        table_name="pro_weekly_report_delivery_runs",
    )
    op.drop_table("pro_weekly_report_delivery_runs")
