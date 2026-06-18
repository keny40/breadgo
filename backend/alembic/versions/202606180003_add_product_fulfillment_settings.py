"""add product fulfillment settings

Revision ID: 202606180003
Revises: 202606180002
Create Date: 2026-06-18 13:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202606180003"
down_revision: Union[str, None] = "202606180002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("products", sa.Column("allow_pickup", sa.Boolean(), nullable=True))
    op.add_column("products", sa.Column("allow_quick_delivery", sa.Boolean(), nullable=True))
    op.add_column("products", sa.Column("allow_parcel_delivery", sa.Boolean(), nullable=True))
    op.add_column("products", sa.Column("quick_delivery_fee", sa.Numeric(10, 2), nullable=True))
    op.add_column("products", sa.Column("parcel_delivery_fee", sa.Numeric(10, 2), nullable=True))

    op.execute("UPDATE products SET allow_pickup = TRUE WHERE allow_pickup IS NULL")
    op.execute("UPDATE products SET allow_quick_delivery = FALSE WHERE allow_quick_delivery IS NULL")
    op.execute("UPDATE products SET allow_parcel_delivery = FALSE WHERE allow_parcel_delivery IS NULL")
    op.execute("UPDATE products SET quick_delivery_fee = 0 WHERE quick_delivery_fee IS NULL")
    op.execute("UPDATE products SET parcel_delivery_fee = 0 WHERE parcel_delivery_fee IS NULL")

    op.alter_column("products", "allow_pickup", nullable=False)
    op.alter_column("products", "allow_quick_delivery", nullable=False)
    op.alter_column("products", "allow_parcel_delivery", nullable=False)
    op.alter_column("products", "quick_delivery_fee", nullable=False)
    op.alter_column("products", "parcel_delivery_fee", nullable=False)


def downgrade() -> None:
    op.drop_column("products", "parcel_delivery_fee")
    op.drop_column("products", "quick_delivery_fee")
    op.drop_column("products", "allow_parcel_delivery")
    op.drop_column("products", "allow_quick_delivery")
    op.drop_column("products", "allow_pickup")
