"""create product templates

Revision ID: 202606180007
Revises: 202606180006
Create Date: 2026-06-18 19:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "202606180007"
down_revision: Union[str, None] = "202606180006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_name", sa.String(length=255), nullable=False),
        sa.Column("day_of_week", sa.Integer(), nullable=False),
        sa.Column("default_stock_quantity", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(timezone=False), nullable=False),
        sa.Column("end_time", sa.Time(timezone=False), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("day_of_week >= 0 AND day_of_week <= 6", name="ck_product_templates_day_of_week"),
        sa.CheckConstraint("default_stock_quantity >= 0", name="ck_product_templates_default_stock_quantity"),
    )
    op.create_index("ix_product_templates_merchant_id", "product_templates", ["merchant_id"], unique=False)
    op.create_index("ix_product_templates_source_product_id", "product_templates", ["source_product_id"], unique=False)
    op.create_index("ix_product_templates_day_of_week", "product_templates", ["day_of_week"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_product_templates_day_of_week", table_name="product_templates")
    op.drop_index("ix_product_templates_source_product_id", table_name="product_templates")
    op.drop_index("ix_product_templates_merchant_id", table_name="product_templates")
    op.drop_table("product_templates")
