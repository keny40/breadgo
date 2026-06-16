"""create products

Revision ID: 202606160003
Revises: 202606160002
Create Date: 2026-06-16 11:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "202606160003"
down_revision: Union[str, None] = "202606160002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    product_status = postgresql.ENUM(
        "ACTIVE",
        "SOLD_OUT",
        "HIDDEN",
        name="product_status",
    )
    product_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("original_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("discount_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("pickup_start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("pickup_end_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "ACTIVE",
                "SOLD_OUT",
                "HIDDEN",
                name="product_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_store_id"), "products", ["store_id"], unique=False)
    op.create_index("ix_products_store_id_status", "products", ["store_id", "status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_products_store_id_status", table_name="products")
    op.drop_index(op.f("ix_products_store_id"), table_name="products")
    op.drop_table("products")
    postgresql.ENUM(name="product_status").drop(op.get_bind(), checkfirst=True)
