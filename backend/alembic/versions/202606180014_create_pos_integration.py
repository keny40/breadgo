"""create pos integration

Revision ID: 202606180014
Revises: 202606180013
Create Date: 2026-06-20 00:14:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "202606180014"
down_revision: str | None = "202606180013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pos_integrations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("provider", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("external_store_code", sa.String(length=120), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sync_status", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pos_integrations_merchant_id"), "pos_integrations", ["merchant_id"], unique=False)
    op.create_index(op.f("ix_pos_integrations_store_id"), "pos_integrations", ["store_id"], unique=False)

    op.create_table(
        "pos_sync_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("integration_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("created_count", sa.Integer(), nullable=False),
        sa.Column("updated_count", sa.Integer(), nullable=False),
        sa.Column("skipped_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["integration_id"], ["pos_integrations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pos_sync_batches_integration_id"), "pos_sync_batches", ["integration_id"], unique=False)
    op.create_index(op.f("ix_pos_sync_batches_merchant_id"), "pos_sync_batches", ["merchant_id"], unique=False)
    op.create_index(op.f("ix_pos_sync_batches_store_id"), "pos_sync_batches", ["store_id"], unique=False)

    op.create_table(
        "pos_sync_rows",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_sku", sa.String(length=120), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["pos_sync_batches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_pos_sync_rows_batch_id"), "pos_sync_rows", ["batch_id"], unique=False)
    op.create_index(op.f("ix_pos_sync_rows_product_id"), "pos_sync_rows", ["product_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_pos_sync_rows_product_id"), table_name="pos_sync_rows")
    op.drop_index(op.f("ix_pos_sync_rows_batch_id"), table_name="pos_sync_rows")
    op.drop_table("pos_sync_rows")
    op.drop_index(op.f("ix_pos_sync_batches_store_id"), table_name="pos_sync_batches")
    op.drop_index(op.f("ix_pos_sync_batches_merchant_id"), table_name="pos_sync_batches")
    op.drop_index(op.f("ix_pos_sync_batches_integration_id"), table_name="pos_sync_batches")
    op.drop_table("pos_sync_batches")
    op.drop_index(op.f("ix_pos_integrations_store_id"), table_name="pos_integrations")
    op.drop_index(op.f("ix_pos_integrations_merchant_id"), table_name="pos_integrations")
    op.drop_table("pos_integrations")
