"""create recommendation usages

Revision ID: 202606180008
Revises: 202606180007
Create Date: 2026-06-18 20:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "202606180008"
down_revision: Union[str, None] = "202606180007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "recommendation_usages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("recommendation_type", sa.String(length=50), nullable=False),
        sa.Column("confidence_label", sa.String(length=20), nullable=False),
        sa.Column("recommended_stock_quantity", sa.Integer(), nullable=False),
        sa.Column("recommended_discount_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("original_stock_quantity", sa.Integer(), nullable=True),
        sa.Column("original_discount_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("action_type", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_product_id"], ["products.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("recommended_stock_quantity >= 0", name="ck_recommendation_usages_stock"),
    )
    op.create_index("ix_recommendation_usages_merchant_id", "recommendation_usages", ["merchant_id"], unique=False)
    op.create_index(
        "ix_recommendation_usages_source_product_id",
        "recommendation_usages",
        ["source_product_id"],
        unique=False,
    )
    op.create_index(
        "ix_recommendation_usages_created_product_id",
        "recommendation_usages",
        ["created_product_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_recommendation_usages_created_product_id", table_name="recommendation_usages")
    op.drop_index("ix_recommendation_usages_source_product_id", table_name="recommendation_usages")
    op.drop_index("ix_recommendation_usages_merchant_id", table_name="recommendation_usages")
    op.drop_table("recommendation_usages")
