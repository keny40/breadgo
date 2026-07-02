"""add merchant application password hash

Revision ID: 202606180026
Revises: 202606180025
Create Date: 2026-06-18 00:26:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "202606180026"
down_revision: str | None = "202606180025"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("merchant_applications", sa.Column("password_hash", sa.String(length=255), nullable=True))
    op.execute("UPDATE merchant_applications SET password_hash = '' WHERE password_hash IS NULL")
    op.alter_column("merchant_applications", "password_hash", nullable=False)


def downgrade() -> None:
    op.drop_column("merchant_applications", "password_hash")
