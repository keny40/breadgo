"""create reservation histories

Revision ID: 202606180004
Revises: 202606180003
Create Date: 2026-06-18 15:30:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "202606180004"
down_revision: Union[str, None] = "202606180003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reservation_histories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reservation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor_role", sa.String(length=32), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("from_status", sa.String(length=64), nullable=True),
        sa.Column("to_status", sa.String(length=64), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reservation_id"], ["reservations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reservation_histories_actor_user_id", "reservation_histories", ["actor_user_id"])
    op.create_index("ix_reservation_histories_event_type", "reservation_histories", ["event_type"])
    op.create_index("ix_reservation_histories_reservation_id", "reservation_histories", ["reservation_id"])


def downgrade() -> None:
    op.drop_index("ix_reservation_histories_reservation_id", table_name="reservation_histories")
    op.drop_index("ix_reservation_histories_event_type", table_name="reservation_histories")
    op.drop_index("ix_reservation_histories_actor_user_id", table_name="reservation_histories")
    op.drop_table("reservation_histories")
