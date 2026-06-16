"""add region fields to stores

Revision ID: 202606160006
Revises: 202606160005
Create Date: 2026-06-16 14:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202606160006"
down_revision: Union[str, None] = "202606160005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("stores", sa.Column("sido", sa.String(length=100), nullable=True))
    op.add_column("stores", sa.Column("sigungu", sa.String(length=100), nullable=True))
    op.add_column("stores", sa.Column("dong", sa.String(length=100), nullable=True))
    op.add_column("stores", sa.Column("latitude", sa.Numeric(9, 6), nullable=True))
    op.add_column("stores", sa.Column("longitude", sa.Numeric(9, 6), nullable=True))
    op.create_index(op.f("ix_stores_sido"), "stores", ["sido"], unique=False)
    op.create_index(op.f("ix_stores_sigungu"), "stores", ["sigungu"], unique=False)
    op.create_index(op.f("ix_stores_dong"), "stores", ["dong"], unique=False)
    op.create_index("ix_stores_region", "stores", ["sido", "sigungu", "dong"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_stores_region", table_name="stores")
    op.drop_index(op.f("ix_stores_dong"), table_name="stores")
    op.drop_index(op.f("ix_stores_sigungu"), table_name="stores")
    op.drop_index(op.f("ix_stores_sido"), table_name="stores")
    op.drop_column("stores", "longitude")
    op.drop_column("stores", "latitude")
    op.drop_column("stores", "dong")
    op.drop_column("stores", "sigungu")
    op.drop_column("stores", "sido")
