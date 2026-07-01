"""create merchant applications

Revision ID: 202606180024
Revises: 202606180023
Create Date: 2026-06-18 00:24:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "202606180024"
down_revision: str | None = "202606180023"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    merchant_application_status = postgresql.ENUM(
        "PENDING",
        "APPROVED",
        "REJECTED",
        name="merchant_application_status",
    )
    merchant_application_status.create(op.get_bind(), checkfirst=True)
    merchant_application_status_column = postgresql.ENUM(
        "PENDING",
        "APPROVED",
        "REJECTED",
        name="merchant_application_status",
        create_type=False,
    )

    op.create_table(
        "merchant_applications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_name", sa.String(length=255), nullable=False),
        sa.Column("owner_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("business_registration_number", sa.String(length=64), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=False),
        sa.Column("region_sido", sa.String(length=100), nullable=True),
        sa.Column("region_sigungu", sa.String(length=100), nullable=True),
        sa.Column("region_dong", sa.String(length=100), nullable=True),
        sa.Column("product_category", sa.String(length=100), nullable=True),
        sa.Column("pickup_available_time", sa.String(length=100), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("status", merchant_application_status_column, nullable=False),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_by_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_merchant_applications_email", "merchant_applications", ["email"])
    op.create_index(
        "ix_merchant_applications_business_registration_number",
        "merchant_applications",
        ["business_registration_number"],
    )
    op.create_index("ix_merchant_applications_status", "merchant_applications", ["status"])
    op.create_index("ix_merchant_applications_merchant_id", "merchant_applications", ["merchant_id"])
    op.create_index(
        "ix_merchant_applications_reviewed_by_user_id",
        "merchant_applications",
        ["reviewed_by_user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_merchant_applications_reviewed_by_user_id", table_name="merchant_applications")
    op.drop_index("ix_merchant_applications_merchant_id", table_name="merchant_applications")
    op.drop_index("ix_merchant_applications_status", table_name="merchant_applications")
    op.drop_index("ix_merchant_applications_business_registration_number", table_name="merchant_applications")
    op.drop_index("ix_merchant_applications_email", table_name="merchant_applications")
    op.drop_table("merchant_applications")
    postgresql.ENUM(name="merchant_application_status").drop(op.get_bind(), checkfirst=True)
