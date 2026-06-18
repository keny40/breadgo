"""add payment provider

Revision ID: 202606180006
Revises: 202606180005
Create Date: 2026-06-18 18:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202606180006"
down_revision: Union[str, None] = "202606180005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("payments", sa.Column("provider", sa.String(length=32), nullable=True))
    op.execute("UPDATE payments SET provider = 'MOCK' WHERE provider IS NULL")
    op.alter_column("payments", "provider", nullable=False)


def downgrade() -> None:
    op.drop_column("payments", "provider")
