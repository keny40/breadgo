"""create product events

Revision ID: 202606180011
Revises: 202606180010
Create Date: 2026-06-18 23:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "202606180011"
down_revision: Union[str, None] = "202606180010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_product_events_product_id", "product_events", ["product_id"], unique=False)
    op.create_index("ix_product_events_store_id", "product_events", ["store_id"], unique=False)
    op.create_index("ix_product_events_merchant_id", "product_events", ["merchant_id"], unique=False)
    op.create_index("ix_product_events_user_id", "product_events", ["user_id"], unique=False)
    op.create_index("ix_product_events_event_type", "product_events", ["event_type"], unique=False)
    op.create_index(
        "ix_product_events_product_type_created",
        "product_events",
        ["product_id", "event_type", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_product_events_product_type_created", table_name="product_events")
    op.drop_index("ix_product_events_event_type", table_name="product_events")
    op.drop_index("ix_product_events_user_id", table_name="product_events")
    op.drop_index("ix_product_events_merchant_id", table_name="product_events")
    op.drop_index("ix_product_events_store_id", table_name="product_events")
    op.drop_index("ix_product_events_product_id", table_name="product_events")
    op.drop_table("product_events")
