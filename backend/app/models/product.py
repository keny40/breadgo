import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.product_template import ProductTemplate
    from app.models.reservation import Reservation
    from app.models.store import Store


class ProductStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SOLD_OUT = "SOLD_OUT"
    HIDDEN = "HIDDEN"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stores.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    external_sku: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    original_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    discount_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    allow_pickup: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_quick_delivery: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_parcel_delivery: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    quick_delivery_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    parcel_delivery_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    pickup_start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    pickup_end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus, name="product_status"),
        nullable=False,
        default=ProductStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    store: Mapped["Store"] = relationship("Store", back_populates="products")
    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation",
        back_populates="product",
    )
    relist_templates: Mapped[list["ProductTemplate"]] = relationship(
        "ProductTemplate",
        back_populates="source_product",
    )
