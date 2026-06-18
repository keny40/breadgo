"""add settlement account fields

Revision ID: 202606180001
Revises: 202606170002
Create Date: 2026-06-18 09:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "202606180001"
down_revision: Union[str, None] = "202606170002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("merchants", sa.Column("bank_name", sa.String(length=100), nullable=True))
    op.add_column("merchants", sa.Column("bank_account_number", sa.String(length=100), nullable=True))
    op.add_column("merchants", sa.Column("bank_account_holder", sa.String(length=100), nullable=True))
    op.add_column("merchants", sa.Column("settlement_cycle", sa.String(length=50), nullable=True))
    op.add_column("merchants", sa.Column("settlement_memo", sa.Text(), nullable=True))
    op.add_column("settlements", sa.Column("admin_memo", sa.Text(), nullable=True))
    op.add_column("settlements", sa.Column("hold_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("settlements", "hold_reason")
    op.drop_column("settlements", "admin_memo")
    op.drop_column("merchants", "settlement_memo")
    op.drop_column("merchants", "settlement_cycle")
    op.drop_column("merchants", "bank_account_holder")
    op.drop_column("merchants", "bank_account_number")
    op.drop_column("merchants", "bank_name")
