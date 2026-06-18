import enum
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.merchant import Merchant
    from app.models.payment import Payment
    from app.models.reservation import Reservation
    from app.models.store import Store


class SettlementStatus(str, enum.Enum):
    PENDING = "PENDING"
    READY = "READY"
    PAID = "PAID"
    HOLD = "HOLD"
    CANCELLED = "CANCELLED"


class Settlement(Base):
    __tablename__ = "settlements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stores.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    reservation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reservations.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    platform_fee_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    platform_fee_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    pg_fee_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    pg_fee_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    merchant_settlement_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[SettlementStatus] = mapped_column(
        Enum(SettlementStatus, name="settlement_status"),
        nullable=False,
        default=SettlementStatus.PENDING,
    )
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    admin_memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    hold_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
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

    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="settlements")
    store: Mapped["Store"] = relationship("Store", back_populates="settlements")
    reservation: Mapped["Reservation"] = relationship("Reservation", back_populates="settlement")
    payment: Mapped["Payment"] = relationship("Payment", back_populates="settlement")
