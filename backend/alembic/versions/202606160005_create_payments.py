"""create payments

Revision ID: 202606160005
Revises: 202606160004
Create Date: 2026-06-16 13:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "202606160005"
down_revision: Union[str, None] = "202606160004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    payment_status = postgresql.ENUM(
        "READY",
        "PAID",
        "FAILED",
        "CANCELLED",
        "REFUNDED",
        name="payment_status",
    )
    payment_method = postgresql.ENUM(
        "MOCK_CARD",
        "MOCK_KAKAO_PAY",
        "MOCK_NAVER_PAY",
        name="payment_method",
    )
    payment_status.create(op.get_bind(), checkfirst=True)
    payment_method.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reservation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "method",
            postgresql.ENUM(
                "MOCK_CARD",
                "MOCK_KAKAO_PAY",
                "MOCK_NAVER_PAY",
                name="payment_method",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "READY",
                "PAID",
                "FAILED",
                "CANCELLED",
                "REFUNDED",
                name="payment_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["reservation_id"], ["reservations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_payments_reservation_id"), "payments", ["reservation_id"], unique=False)
    op.create_index(op.f("ix_payments_user_id"), "payments", ["user_id"], unique=False)
    op.create_index("ix_payments_reservation_id_status", "payments", ["reservation_id", "status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_payments_reservation_id_status", table_name="payments")
    op.drop_index(op.f("ix_payments_user_id"), table_name="payments")
    op.drop_index(op.f("ix_payments_reservation_id"), table_name="payments")
    op.drop_table("payments")
    postgresql.ENUM(name="payment_method").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="payment_status").drop(op.get_bind(), checkfirst=True)
