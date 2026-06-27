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


class ProWeeklyReportSnapshot(Base):
    __tablename__ = "pro_weekly_report_snapshots"
    __table_args__ = (
        UniqueConstraint("merchant_id", "start_date", "end_date", name="uq_pro_weekly_report_snapshot_period"),
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
    start_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    total_sales_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    total_reservation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_picked_up_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_cancelled_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_saved_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_unresolved_alert_count: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=Decimal("0.00"))
    high_severity_alert_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_recommendation_action_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_inventory_event_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pos_sync_issue_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    csv_import_error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    text_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
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
    insights: Mapped[list["ProWeeklyReportInsight"]] = relationship(
        "ProWeeklyReportInsight",
        back_populates="snapshot",
        cascade="all, delete-orphan",
        order_by="ProWeeklyReportInsight.created_at.asc()",
    )


class ProWeeklyReportInsight(Base):
    __tablename__ = "pro_weekly_report_insights"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pro_weekly_report_snapshots.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    snapshot: Mapped["ProWeeklyReportSnapshot"] = relationship("ProWeeklyReportSnapshot", back_populates="insights")


class ProWeeklyReportBatchRun(Base):
    __tablename__ = "pro_weekly_report_batch_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_type: Mapped[str] = mapped_column(String(40), nullable=False, default="MANUAL_TEST")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="STARTED")
    start_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    target_merchant_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    items: Mapped[list["ProWeeklyReportBatchRunItem"]] = relationship(
        "ProWeeklyReportBatchRunItem",
        back_populates="batch_run",
        cascade="all, delete-orphan",
        order_by="ProWeeklyReportBatchRunItem.created_at.asc()",
    )


class ProWeeklyReportBatchRunItem(Base):
    __tablename__ = "pro_weekly_report_batch_run_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pro_weekly_report_batch_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pro_weekly_report_snapshots.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    batch_run: Mapped["ProWeeklyReportBatchRun"] = relationship("ProWeeklyReportBatchRun", back_populates="items")
    merchant: Mapped["Merchant"] = relationship("Merchant")
    snapshot: Mapped["ProWeeklyReportSnapshot | None"] = relationship("ProWeeklyReportSnapshot")


class ProWeeklyReportDeliveryRun(Base):
    __tablename__ = "pro_weekly_report_delivery_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_type: Mapped[str] = mapped_column(String(40), nullable=False, default="PREVIEW")
    channel: Mapped[str] = mapped_column(String(40), nullable=False, default="IN_APP_PREVIEW")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="PENDING")
    period_start: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    total_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ready_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    items: Mapped[list["ProWeeklyReportDeliveryRunItem"]] = relationship(
        "ProWeeklyReportDeliveryRunItem",
        back_populates="delivery_run",
        cascade="all, delete-orphan",
        order_by="ProWeeklyReportDeliveryRunItem.created_at.asc()",
    )


class ProWeeklyReportDeliveryRunItem(Base):
    __tablename__ = "pro_weekly_report_delivery_run_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    delivery_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pro_weekly_report_delivery_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    merchant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("merchants.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pro_weekly_report_snapshots.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    delivery_run: Mapped["ProWeeklyReportDeliveryRun"] = relationship(
        "ProWeeklyReportDeliveryRun",
        back_populates="items",
    )
    merchant: Mapped["Merchant"] = relationship("Merchant")
    snapshot: Mapped["ProWeeklyReportSnapshot | None"] = relationship("ProWeeklyReportSnapshot")
