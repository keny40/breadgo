"""create weekly report batch runs

Revision ID: 202606180019
Revises: 202606180018
Create Date: 2026-06-22 00:19:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "202606180019"
down_revision: str | None = "202606180018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pro_weekly_report_batch_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("target_merchant_count", sa.Integer(), nullable=False),
        sa.Column("success_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("skipped_count", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pro_weekly_report_batch_runs_start_date"),
        "pro_weekly_report_batch_runs",
        ["start_date"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pro_weekly_report_batch_runs_end_date"),
        "pro_weekly_report_batch_runs",
        ["end_date"],
        unique=False,
    )

    op.create_table(
        "pro_weekly_report_batch_run_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("batch_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["batch_run_id"], ["pro_weekly_report_batch_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["snapshot_id"], ["pro_weekly_report_snapshots.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_pro_weekly_report_batch_run_items_batch_run_id"),
        "pro_weekly_report_batch_run_items",
        ["batch_run_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pro_weekly_report_batch_run_items_merchant_id"),
        "pro_weekly_report_batch_run_items",
        ["merchant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_pro_weekly_report_batch_run_items_snapshot_id"),
        "pro_weekly_report_batch_run_items",
        ["snapshot_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_pro_weekly_report_batch_run_items_snapshot_id"), table_name="pro_weekly_report_batch_run_items")
    op.drop_index(op.f("ix_pro_weekly_report_batch_run_items_merchant_id"), table_name="pro_weekly_report_batch_run_items")
    op.drop_index(op.f("ix_pro_weekly_report_batch_run_items_batch_run_id"), table_name="pro_weekly_report_batch_run_items")
    op.drop_table("pro_weekly_report_batch_run_items")
    op.drop_index(op.f("ix_pro_weekly_report_batch_runs_end_date"), table_name="pro_weekly_report_batch_runs")
    op.drop_index(op.f("ix_pro_weekly_report_batch_runs_start_date"), table_name="pro_weekly_report_batch_runs")
    op.drop_table("pro_weekly_report_batch_runs")
