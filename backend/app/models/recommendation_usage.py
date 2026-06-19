import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.merchant import Merchant
    from app.models.product import Product


class RecommendationUsage(Base):
    __tablename__ = "recommendation_usages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    source_product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    created_product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    recommendation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_label: Mapped[str] = mapped_column(String(20), nullable=False)
    recommended_stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    recommended_discount_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    original_stock_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    original_discount_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    accepted_stock_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    accepted_discount_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    stock_delta: Mapped[int | None] = mapped_column(Integer, nullable=True)
    discount_price_delta: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    adoption_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    draft_product_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_reserved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    first_picked_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="recommendation_usages")
    source_product: Mapped["Product"] = relationship("Product", foreign_keys=[source_product_id])
    created_product: Mapped["Product | None"] = relationship("Product", foreign_keys=[created_product_id])
