"""add recommendation funnel fields

Revision ID: 202606180010
Revises: 202606180009
Create Date: 2026-06-18 22:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202606180010"
down_revision: Union[str, None] = "202606180009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("recommendation_usages", sa.Column("draft_product_status", sa.String(length=50), nullable=True))
    op.add_column("recommendation_usages", sa.Column("published_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("recommendation_usages", sa.Column("first_reserved_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("recommendation_usages", sa.Column("first_paid_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("recommendation_usages", sa.Column("first_picked_up_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("recommendation_usages", "first_picked_up_at")
    op.drop_column("recommendation_usages", "first_paid_at")
    op.drop_column("recommendation_usages", "first_reserved_at")
    op.drop_column("recommendation_usages", "published_at")
    op.drop_column("recommendation_usages", "draft_product_status")
