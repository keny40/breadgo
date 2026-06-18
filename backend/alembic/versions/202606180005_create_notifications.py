"""create notifications

Revision ID: 202606180005
Revises: 202606180004
Create Date: 2026-06-18 16:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "202606180005"
down_revision: Union[str, None] = "202606180004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("notification_type", sa.String(length=64), nullable=False),
        sa.Column("related_reservation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("related_payment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("related_settlement_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["related_payment_id"], ["payments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["related_reservation_id"], ["reservations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["related_settlement_id"], ["settlements.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])
    op.create_index("ix_notifications_role", "notifications", ["role"])
    op.create_index("ix_notifications_notification_type", "notifications", ["notification_type"])
    op.create_index("ix_notifications_related_reservation_id", "notifications", ["related_reservation_id"])
    op.create_index("ix_notifications_related_payment_id", "notifications", ["related_payment_id"])
    op.create_index("ix_notifications_related_settlement_id", "notifications", ["related_settlement_id"])


def downgrade() -> None:
    op.drop_index("ix_notifications_related_settlement_id", table_name="notifications")
    op.drop_index("ix_notifications_related_payment_id", table_name="notifications")
    op.drop_index("ix_notifications_related_reservation_id", table_name="notifications")
    op.drop_index("ix_notifications_notification_type", table_name="notifications")
    op.drop_index("ix_notifications_role", table_name="notifications")
    op.drop_index("ix_notifications_user_id", table_name="notifications")
    op.drop_table("notifications")
