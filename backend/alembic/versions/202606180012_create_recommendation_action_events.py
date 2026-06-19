"""create recommendation action events

Revision ID: 202606180012
Revises: 202606180011
Create Date: 2026-06-19 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "202606180012"
down_revision: Union[str, None] = "202606180011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "recommendation_action_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("recommendation_type", sa.String(length=50), nullable=True),
        sa.Column("action_priority", sa.String(length=20), nullable=True),
        sa.Column("risk_label", sa.String(length=50), nullable=True),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("created_product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_product_id"], ["products.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_recommendation_action_events_merchant_id", "recommendation_action_events", ["merchant_id"])
    op.create_index("ix_recommendation_action_events_product_id", "recommendation_action_events", ["product_id"])
    op.create_index(
        "ix_recommendation_action_events_created_product_id",
        "recommendation_action_events",
        ["created_product_id"],
    )
    op.create_index("ix_recommendation_action_events_event_type", "recommendation_action_events", ["event_type"])
    op.create_index(
        "ix_recommendation_action_events_merchant_event_created",
        "recommendation_action_events",
        ["merchant_id", "event_type", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_recommendation_action_events_merchant_event_created", table_name="recommendation_action_events")
    op.drop_index("ix_recommendation_action_events_event_type", table_name="recommendation_action_events")
    op.drop_index("ix_recommendation_action_events_created_product_id", table_name="recommendation_action_events")
    op.drop_index("ix_recommendation_action_events_product_id", table_name="recommendation_action_events")
    op.drop_index("ix_recommendation_action_events_merchant_id", table_name="recommendation_action_events")
    op.drop_table("recommendation_action_events")
