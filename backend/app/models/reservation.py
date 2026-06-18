import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.payment import Payment
    from app.models.product import Product
    from app.models.reservation_history import ReservationHistory
    from app.models.settlement import Settlement
    from app.models.store import Store
    from app.models.user import User


class ReservationStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    PICKED_UP = "PICKED_UP"
    EXPIRED = "EXPIRED"


class FulfillmentMethod(str, enum.Enum):
    PICKUP = "PICKUP"
    QUICK_DELIVERY = "QUICK_DELIVERY"
    PARCEL_DELIVERY = "PARCEL_DELIVERY"


class DeliveryStatus(str, enum.Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    REQUESTED = "REQUESTED"
    PREPARING = "PREPARING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stores.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    product_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    delivery_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fulfillment_method: Mapped[FulfillmentMethod] = mapped_column(
        Enum(FulfillmentMethod, name="fulfillment_method"),
        nullable=False,
        default=FulfillmentMethod.PICKUP,
    )
    recipient_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recipient_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    delivery_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    delivery_request_memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery_status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus, name="delivery_status"),
        nullable=False,
        default=DeliveryStatus.NOT_REQUIRED,
    )
    status: Mapped[ReservationStatus] = mapped_column(
        Enum(ReservationStatus, name="reservation_status"),
        nullable=False,
        default=ReservationStatus.PENDING,
    )
    pickup_code: Mapped[str] = mapped_column(String(6), unique=True, index=True, nullable=False)
    reserved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    pickup_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
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

    user: Mapped["User"] = relationship("User", back_populates="reservations")
    product: Mapped["Product"] = relationship("Product", back_populates="reservations")
    store: Mapped["Store"] = relationship("Store", back_populates="reservations")
    payment: Mapped["Payment | None"] = relationship(
        "Payment",
        back_populates="reservation",
        uselist=False,
    )
    settlement: Mapped["Settlement | None"] = relationship(
        "Settlement",
        back_populates="reservation",
        uselist=False,
    )
    history_events: Mapped[list["ReservationHistory"]] = relationship(
        "ReservationHistory",
        back_populates="reservation",
        cascade="all, delete-orphan",
        order_by="ReservationHistory.created_at",
    )
