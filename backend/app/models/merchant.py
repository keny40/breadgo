import enum
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.product_template import ProductTemplate
    from app.models.recommendation_usage import RecommendationUsage
    from app.models.settlement import Settlement
    from app.models.store import Store
    from app.models.user import User


class MerchantStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SUSPENDED = "SUSPENDED"


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    business_registration_number: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )
    representative_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(32), nullable=False)
    bank_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bank_account_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bank_account_holder: Mapped[str | None] = mapped_column(String(100), nullable=True)
    settlement_cycle: Mapped[str | None] = mapped_column(String(50), nullable=True)
    settlement_memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[MerchantStatus] = mapped_column(
        Enum(MerchantStatus, name="merchant_status"),
        nullable=False,
        default=MerchantStatus.PENDING,
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

    user: Mapped["User"] = relationship("User", back_populates="merchant")
    stores: Mapped[list["Store"]] = relationship(
        "Store",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )
    settlements: Mapped[list["Settlement"]] = relationship(
        "Settlement",
        back_populates="merchant",
    )
    product_templates: Mapped[list["ProductTemplate"]] = relationship(
        "ProductTemplate",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )
    recommendation_usages: Mapped[list["RecommendationUsage"]] = relationship(
        "RecommendationUsage",
        back_populates="merchant",
        cascade="all, delete-orphan",
    )
