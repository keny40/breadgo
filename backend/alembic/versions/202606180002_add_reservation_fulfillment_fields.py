"""add reservation fulfillment fields

Revision ID: 202606180002
Revises: 202606180001
Create Date: 2026-06-18 11:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "202606180002"
down_revision: Union[str, None] = "202606180001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    fulfillment_method = postgresql.ENUM(
        "PICKUP",
        "QUICK_DELIVERY",
        "PARCEL_DELIVERY",
        name="fulfillment_method",
    )
    delivery_status = postgresql.ENUM(
        "NOT_REQUIRED",
        "REQUESTED",
        "PREPARING",
        "SENT",
        "DELIVERED",
        "CANCELLED",
        name="delivery_status",
    )
    fulfillment_method.create(op.get_bind(), checkfirst=True)
    delivery_status.create(op.get_bind(), checkfirst=True)

    op.add_column("reservations", sa.Column("product_amount", sa.Numeric(10, 2), nullable=True))
    op.add_column("reservations", sa.Column("delivery_fee", sa.Numeric(10, 2), nullable=True))
    op.add_column(
        "reservations",
        sa.Column(
            "fulfillment_method",
            postgresql.ENUM(
                "PICKUP",
                "QUICK_DELIVERY",
                "PARCEL_DELIVERY",
                name="fulfillment_method",
                create_type=False,
            ),
            nullable=True,
        ),
    )
    op.add_column("reservations", sa.Column("recipient_name", sa.String(length=255), nullable=True))
    op.add_column("reservations", sa.Column("recipient_phone", sa.String(length=32), nullable=True))
    op.add_column("reservations", sa.Column("delivery_address", sa.String(length=500), nullable=True))
    op.add_column("reservations", sa.Column("delivery_request_memo", sa.Text(), nullable=True))
    op.add_column(
        "reservations",
        sa.Column(
            "delivery_status",
            postgresql.ENUM(
                "NOT_REQUIRED",
                "REQUESTED",
                "PREPARING",
                "SENT",
                "DELIVERED",
                "CANCELLED",
                name="delivery_status",
                create_type=False,
            ),
            nullable=True,
        ),
    )

    op.execute("UPDATE reservations SET product_amount = total_price WHERE product_amount IS NULL")
    op.execute("UPDATE reservations SET delivery_fee = 0 WHERE delivery_fee IS NULL")
    op.execute("UPDATE reservations SET fulfillment_method = 'PICKUP' WHERE fulfillment_method IS NULL")
    op.execute("UPDATE reservations SET delivery_status = 'NOT_REQUIRED' WHERE delivery_status IS NULL")

    op.alter_column("reservations", "product_amount", nullable=False)
    op.alter_column("reservations", "delivery_fee", nullable=False)
    op.alter_column("reservations", "fulfillment_method", nullable=False)
    op.alter_column("reservations", "delivery_status", nullable=False)


def downgrade() -> None:
    op.drop_column("reservations", "delivery_status")
    op.drop_column("reservations", "delivery_request_memo")
    op.drop_column("reservations", "delivery_address")
    op.drop_column("reservations", "recipient_phone")
    op.drop_column("reservations", "recipient_name")
    op.drop_column("reservations", "fulfillment_method")
    op.drop_column("reservations", "delivery_fee")
    op.drop_column("reservations", "product_amount")
    postgresql.ENUM(name="delivery_status").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="fulfillment_method").drop(op.get_bind(), checkfirst=True)
