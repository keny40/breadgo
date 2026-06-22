"""create inventory alert actions

Revision ID: 202606180016
Revises: 202606180015
Create Date: 2026-06-22 00:16:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "202606180016"
down_revision: str | None = "202606180015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "inventory_alert_actions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("alert_type", sa.String(length=80), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("action_type", sa.String(length=40), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventory_alert_actions_action_type"), "inventory_alert_actions", ["action_type"], unique=False)
    op.create_index(op.f("ix_inventory_alert_actions_alert_type"), "inventory_alert_actions", ["alert_type"], unique=False)
    op.create_index(op.f("ix_inventory_alert_actions_merchant_id"), "inventory_alert_actions", ["merchant_id"], unique=False)
    op.create_index(op.f("ix_inventory_alert_actions_product_id"), "inventory_alert_actions", ["product_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_inventory_alert_actions_product_id"), table_name="inventory_alert_actions")
    op.drop_index(op.f("ix_inventory_alert_actions_merchant_id"), table_name="inventory_alert_actions")
    op.drop_index(op.f("ix_inventory_alert_actions_alert_type"), table_name="inventory_alert_actions")
    op.drop_index(op.f("ix_inventory_alert_actions_action_type"), table_name="inventory_alert_actions")
    op.drop_table("inventory_alert_actions")
