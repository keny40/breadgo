"""create settlements

Revision ID: 202606170002
Revises: 202606170001
Create Date: 2026-06-17 18:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "202606170002"
down_revision: Union[str, None] = "202606170001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    settlement_status = postgresql.ENUM(
        "PENDING",
        "READY",
        "PAID",
        "HOLD",
        "CANCELLED",
        name="settlement_status",
    )
    settlement_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "settlements",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reservation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("gross_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("platform_fee_rate", sa.Numeric(5, 4), nullable=False),
        sa.Column("platform_fee_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("pg_fee_rate", sa.Numeric(5, 4), nullable=False),
        sa.Column("pg_fee_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("merchant_settlement_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "PENDING",
                "READY",
                "PAID",
                "HOLD",
                "CANCELLED",
                name="settlement_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reservation_id"], ["reservations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["payment_id"], ["payments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("payment_id", name="uq_settlements_payment_id"),
        sa.UniqueConstraint("reservation_id", name="uq_settlements_reservation_id"),
    )
    op.create_index(op.f("ix_settlements_merchant_id"), "settlements", ["merchant_id"], unique=False)
    op.create_index(op.f("ix_settlements_store_id"), "settlements", ["store_id"], unique=False)
    op.create_index(op.f("ix_settlements_reservation_id"), "settlements", ["reservation_id"], unique=False)
    op.create_index(op.f("ix_settlements_payment_id"), "settlements", ["payment_id"], unique=False)
    op.create_index("ix_settlements_status_created_at", "settlements", ["status", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_settlements_status_created_at", table_name="settlements")
    op.drop_index(op.f("ix_settlements_payment_id"), table_name="settlements")
    op.drop_index(op.f("ix_settlements_reservation_id"), table_name="settlements")
    op.drop_index(op.f("ix_settlements_store_id"), table_name="settlements")
    op.drop_index(op.f("ix_settlements_merchant_id"), table_name="settlements")
    op.drop_table("settlements")
    postgresql.ENUM(name="settlement_status").drop(op.get_bind(), checkfirst=True)
