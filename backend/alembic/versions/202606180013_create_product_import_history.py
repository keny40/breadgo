"""create product import history

Revision ID: 202606180013
Revises: 202606180012
Create Date: 2026-06-20 00:13:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "202606180013"
down_revision: str | None = "202606180012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("products", sa.Column("external_sku", sa.String(length=120), nullable=True))
    op.create_index(op.f("ix_products_external_sku"), "products", ["external_sku"], unique=False)

    op.create_table(
        "product_import_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merchant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("success_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("created_count", sa.Integer(), nullable=False),
        sa.Column("updated_count", sa.Integer(), nullable=False),
        sa.Column("skipped_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["merchant_id"], ["merchants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_import_batches_merchant_id"), "product_import_batches", ["merchant_id"], unique=False)
    op.create_index(op.f("ix_product_import_batches_store_id"), "product_import_batches", ["store_id"], unique=False)

    op.create_table(
        "product_import_rows",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["batch_id"], ["product_import_batches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_import_rows_batch_id"), "product_import_rows", ["batch_id"], unique=False)
    op.create_index(op.f("ix_product_import_rows_product_id"), "product_import_rows", ["product_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_product_import_rows_product_id"), table_name="product_import_rows")
    op.drop_index(op.f("ix_product_import_rows_batch_id"), table_name="product_import_rows")
    op.drop_table("product_import_rows")
    op.drop_index(op.f("ix_product_import_batches_store_id"), table_name="product_import_batches")
    op.drop_index(op.f("ix_product_import_batches_merchant_id"), table_name="product_import_batches")
    op.drop_table("product_import_batches")
    op.drop_index(op.f("ix_products_external_sku"), table_name="products")
    op.drop_column("products", "external_sku")
