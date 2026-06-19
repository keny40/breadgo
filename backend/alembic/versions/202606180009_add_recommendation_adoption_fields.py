"""add recommendation adoption fields

Revision ID: 202606180009
Revises: 202606180008
Create Date: 2026-06-18 21:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202606180009"
down_revision: Union[str, None] = "202606180008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("recommendation_usages", sa.Column("accepted_stock_quantity", sa.Integer(), nullable=True))
    op.add_column("recommendation_usages", sa.Column("accepted_discount_price", sa.Numeric(10, 2), nullable=True))
    op.add_column("recommendation_usages", sa.Column("stock_delta", sa.Integer(), nullable=True))
    op.add_column("recommendation_usages", sa.Column("discount_price_delta", sa.Numeric(10, 2), nullable=True))
    op.add_column("recommendation_usages", sa.Column("adoption_type", sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column("recommendation_usages", "adoption_type")
    op.drop_column("recommendation_usages", "discount_price_delta")
    op.drop_column("recommendation_usages", "stock_delta")
    op.drop_column("recommendation_usages", "accepted_discount_price")
    op.drop_column("recommendation_usages", "accepted_stock_quantity")
