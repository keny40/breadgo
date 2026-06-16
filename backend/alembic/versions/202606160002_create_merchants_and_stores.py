"""create merchants and stores

Revision ID: 202606160002
Revises: 202606160001
Create Date: 2026-06-16 10:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "202606160002"
down_revision: Union[str, None] = "202606160001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    merchant_status = postgresql.ENUM(
        "PENDING",
        "APPROVED",
        "REJECTED",
        "SUSPENDED",
        name="merchant_status",
    )
    merchant_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "merchants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_name", sa.String(length=255), nullable=False),
        sa.Column("business_registration_number", sa.String(length=64), nullable=False),
        sa.Column("representative_name", sa.String(length=255), nullable=False),
        sa.Column("phone_number", sa.String(length=32), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "PENDING",
                "APPROVED",
                "REJECTED",
                "SUSPENDED",
                name="merchant_status",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_merchants_user_id"),
        sa.UniqueConstraint(
            "business_registration_number",
            name="uq_merchants_business_registration_number",
        ),
    )
    op.create_index(op.f("ix_merchants_user_id"), "merchants", ["user_id"], unique=True)
    op.create_index(
        op.f("ix_merchants_business_registration_number"),
        "merchants",
        ["business_registration_number"],
        unique=True,
    )

    op.create_table(
        "stores",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("address_detail", sa.String(length=255), nullable=True),
        sa.Column("phone_number", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("opening_time", sa.Time(), nullable=False),
        sa.Column("closing_time", sa.Time(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_stores_merchant_id"), "stores", ["merchant_id"], unique=False)
    op.create_index("ix_stores_merchant_id_is_active", "stores", ["merchant_id", "is_active"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_stores_merchant_id_is_active", table_name="stores")
    op.drop_index(op.f("ix_stores_merchant_id"), table_name="stores")
    op.drop_table("stores")
    op.drop_index(op.f("ix_merchants_business_registration_number"), table_name="merchants")
    op.drop_index(op.f("ix_merchants_user_id"), table_name="merchants")
    op.drop_table("merchants")
    postgresql.ENUM(name="merchant_status").drop(op.get_bind(), checkfirst=True)
