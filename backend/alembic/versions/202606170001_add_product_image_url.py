"""add product image url

Revision ID: 202606170001
Revises: 202606160006
Create Date: 2026-06-17 10:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202606170001"
down_revision: Union[str, None] = "202606160006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("products", sa.Column("image_url", sa.String(length=1000), nullable=True))


def downgrade() -> None:
    op.drop_column("products", "image_url")
