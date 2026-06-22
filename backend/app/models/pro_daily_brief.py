import uuid
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.merchant import Merchant
    from app.models.store import Store


class ProDailyBriefSnapshot(Base):
    __tablename__ = "pro_daily_brief_snapshots"
    __table_args__ = (
        UniqueConstraint("merchant_id", "brief_date", name="uq_pro_daily_brief_snapshot_merchant_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    store_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stores.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    brief_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    today_sales_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    today_reservation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    today_picked_up_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    today_cancelled_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    saved_quantity_today: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unresolved_alert_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    action_started_alert_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    high_severity_alert_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    recommendation_action_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pos_last_sync_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    pos_last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    csv_recent_import_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    csv_recent_failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    inventory_event_count_today: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
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

    merchant: Mapped["Merchant"] = relationship("Merchant")
    store: Mapped["Store | None"] = relationship("Store")
    tasks: Mapped[list["ProDailyBriefTask"]] = relationship(
        "ProDailyBriefTask",
        back_populates="snapshot",
        cascade="all, delete-orphan",
        order_by="ProDailyBriefTask.created_at.asc()",
    )


class ProDailyBriefTask(Base):
    __tablename__ = "pro_daily_brief_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pro_daily_brief_snapshots.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    task_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    action_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    action_href: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    snapshot: Mapped["ProDailyBriefSnapshot"] = relationship("ProDailyBriefSnapshot", back_populates="tasks")
