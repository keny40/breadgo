"""create product inventory events

Revision ID: 202606180015
Revises: 202606180014
Create Date: 2026-06-20 00:15:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "202606180015"
down_revision: str | None = "202606180014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "product_inventory_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=60), nullable=False),
        sa.Column("quantity_before", sa.Integer(), nullable=True),
        sa.Column("quantity_after", sa.Integer(), nullable=True),
        sa.Column("quantity_delta", sa.Integer(), nullable=True),
        sa.Column("source_type", sa.String(length=40), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_inventory_events_event_type"), "product_inventory_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_product_inventory_events_merchant_id"), "product_inventory_events", ["merchant_id"], unique=False)
    op.create_index(op.f("ix_product_inventory_events_product_id"), "product_inventory_events", ["product_id"], unique=False)
    op.create_index(op.f("ix_product_inventory_events_source_type"), "product_inventory_events", ["source_type"], unique=False)
    op.create_index(op.f("ix_product_inventory_events_store_id"), "product_inventory_events", ["store_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_product_inventory_events_store_id"), table_name="product_inventory_events")
    op.drop_index(op.f("ix_product_inventory_events_source_type"), table_name="product_inventory_events")
    op.drop_index(op.f("ix_product_inventory_events_product_id"), table_name="product_inventory_events")
    op.drop_index(op.f("ix_product_inventory_events_merchant_id"), table_name="product_inventory_events")
    op.drop_index(op.f("ix_product_inventory_events_event_type"), table_name="product_inventory_events")
    op.drop_table("product_inventory_events")
