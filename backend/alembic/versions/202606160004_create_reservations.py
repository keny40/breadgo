"""create reservations

Revision ID: 202606160004
Revises: 202606160003
Create Date: 2026-06-16 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "202606160004"
down_revision: Union[str, None] = "202606160003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    reservation_status = postgresql.ENUM(
        "PENDING",
        "CONFIRMED",
        "CANCELLED",
        "PICKED_UP",
        "EXPIRED",
        name="reservation_status",
    )
    reservation_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "reservations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "PENDING",
                "CONFIRMED",
                "CANCELLED",
                "PICKED_UP",
                "EXPIRED",
                name="reservation_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("pickup_code", sa.String(length=6), nullable=False),
        sa.Column("reserved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("pickup_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reservations_pickup_code"), "reservations", ["pickup_code"], unique=True)
    op.create_index(op.f("ix_reservations_product_id"), "reservations", ["product_id"], unique=False)
    op.create_index(op.f("ix_reservations_store_id"), "reservations", ["store_id"], unique=False)
    op.create_index(op.f("ix_reservations_user_id"), "reservations", ["user_id"], unique=False)
    op.create_index(
        "ix_reservations_store_id_status",
        "reservations",
        ["store_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_reservations_store_id_status", table_name="reservations")
    op.drop_index(op.f("ix_reservations_user_id"), table_name="reservations")
    op.drop_index(op.f("ix_reservations_store_id"), table_name="reservations")
    op.drop_index(op.f("ix_reservations_product_id"), table_name="reservations")
    op.drop_index(op.f("ix_reservations_pickup_code"), table_name="reservations")
    op.drop_table("reservations")
    postgresql.ENUM(name="reservation_status").drop(op.get_bind(), checkfirst=True)
