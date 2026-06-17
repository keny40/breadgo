import uuid
from datetime import datetime, time, timezone
from typing import TYPE_CHECKING

from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.merchant import Merchant
    from app.models.product import Product
    from app.models.reservation import Reservation
    from app.models.settlement import Settlement


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    address_detail: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sido: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    sigungu: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    dong: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    opening_time: Mapped[time] = mapped_column(Time, nullable=False)
    closing_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
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

    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="stores")
    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="store",
        cascade="all, delete-orphan",
    )
    reservations: Mapped[list["Reservation"]] = relationship(
        "Reservation",
        back_populates="store",
    )
    settlements: Mapped[list["Settlement"]] = relationship(
        "Settlement",
        back_populates="store",
    )
