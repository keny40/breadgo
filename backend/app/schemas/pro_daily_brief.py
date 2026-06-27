from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProDailyBriefTaskRead(BaseModel):
    task_type: str
    priority: str
    title: str
    message: str
    action_label: str
    action_href: str


class MerchantProDailyBriefRead(BaseModel):
    date: date
    today_sales_amount: Decimal
    today_reservation_count: int
    today_picked_up_count: int
    today_cancelled_count: int
    saved_quantity_today: int
    unresolved_alert_count: int
    action_started_alert_count: int
    high_severity_alert_count: int
    recommendation_action_count: int
    pos_last_sync_status: str | None = None
    pos_last_synced_at: datetime | None = None
    csv_recent_import_count: int
    csv_recent_failed_count: int
    inventory_event_count_today: int
    tasks: list[ProDailyBriefTaskRead]


class ProDailyBriefSnapshotTaskRead(BaseModel):
    id: UUID
    snapshot_id: UUID
    task_type: str
    priority: str
    title: str
    message: str
    action_label: str | None = None
    action_href: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProDailyBriefSnapshotRead(BaseModel):
    id: UUID
    merchant_id: UUID
    store_id: UUID | None = None
    brief_date: date
    today_sales_amount: Decimal
    today_reservation_count: int
    today_picked_up_count: int
    today_cancelled_count: int
    saved_quantity_today: int
    unresolved_alert_count: int
    action_started_alert_count: int
    high_severity_alert_count: int
    recommendation_action_count: int
    pos_last_sync_status: str | None = None
    pos_last_synced_at: datetime | None = None
    csv_recent_import_count: int
    csv_recent_failed_count: int
    inventory_event_count_today: int
    created_at: datetime
    updated_at: datetime
    tasks: list[ProDailyBriefSnapshotTaskRead]

    model_config = ConfigDict(from_attributes=True)


class ProDailyBriefHistoryDeltaRead(BaseModel):
    unresolved_alert_delta: int | None = None
    sales_delta: Decimal | None = None
    reservation_delta: int | None = None
    picked_up_delta: int | None = None
    saved_quantity_delta: int | None = None


class MerchantProDailyBriefHistoryRead(BaseModel):
    snapshots: list[ProDailyBriefSnapshotRead]
    latest_snapshot_id: UUID | None = None
    previous_snapshot_id: UUID | None = None
    delta: ProDailyBriefHistoryDeltaRead


class ProWeeklyReportDailyTrendRead(BaseModel):
    date: date
    sales_amount: Decimal
    reservation_count: int
    picked_up_count: int
    cancelled_count: int
    saved_quantity: int
    unresolved_alert_count: int
    recommendation_action_count: int


class ProWeeklyReportInsightRead(BaseModel):
    title: str
    message: str
    severity: str = "INFO"


class MerchantProWeeklyReportRead(BaseModel):
    start_date: date
    end_date: date
    total_sales_amount: Decimal
    total_reservation_count: int
    total_picked_up_count: int
    total_cancelled_count: int
    total_saved_quantity: int
    average_unresolved_alert_count: float
    high_severity_alert_count: int
    total_recommendation_action_count: int
    total_inventory_event_count: int
    pos_sync_issue_count: int
    csv_import_error_count: int
    snapshot_days_count: int
    daily_trends: list[ProWeeklyReportDailyTrendRead]
    insights: list[ProWeeklyReportInsightRead]


class ProWeeklyReportSnapshotInsightRead(BaseModel):
    id: UUID
    snapshot_id: UUID
    title: str | None = None
    message: str
    severity: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProWeeklyReportSnapshotRead(BaseModel):
    id: UUID
    merchant_id: UUID
    store_id: UUID | None = None
    start_date: date
    end_date: date
    total_sales_amount: Decimal
    total_reservation_count: int
    total_picked_up_count: int
    total_cancelled_count: int
    total_saved_quantity: int
    average_unresolved_alert_count: Decimal
    high_severity_alert_count: int
    total_recommendation_action_count: int
    total_inventory_event_count: int
    pos_sync_issue_count: int
    csv_import_error_count: int
    text_summary: str | None = None
    created_at: datetime
    updated_at: datetime
    insights: list[ProWeeklyReportSnapshotInsightRead]

    model_config = ConfigDict(from_attributes=True)


class MerchantProWeeklyReportHistoryRead(BaseModel):
    snapshots: list[ProWeeklyReportSnapshotRead]


class ProWeeklyReportAutoSnapshotPreviewRead(BaseModel):
    start_date: date
    end_date: date
    would_create_new: bool
    existing_snapshot_id: UUID | None = None
    report_summary: MerchantProWeeklyReportRead
    insights: list[ProWeeklyReportInsightRead]


class ProWeeklyReportAutoSnapshotRunRead(BaseModel):
    snapshot_id: UUID
    created_or_updated: str
    start_date: date
    end_date: date
    message: str


class ProWeeklyReportBatchRunItemRead(BaseModel):
    id: UUID
    batch_run_id: UUID
    merchant_id: UUID
    snapshot_id: UUID | None = None
    status: str
    message: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProWeeklyReportBatchRunRead(BaseModel):
    id: UUID
    run_type: str
    status: str
    start_date: date
    end_date: date
    target_merchant_count: int
    success_count: int
    failed_count: int
    skipped_count: int
    message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
    items: list[ProWeeklyReportBatchRunItemRead]

    model_config = ConfigDict(from_attributes=True)


class MerchantProWeeklyReportBatchRunHistoryRead(BaseModel):
    batch_runs: list[ProWeeklyReportBatchRunRead]


class AdminProWeeklyReportBatchRunSummaryRead(BaseModel):
    total_runs: int
    completed_count: int
    failed_count: int
    partial_count: int
    latest_run_status: str | None = None
    latest_run_at: datetime | None = None


class AdminProWeeklyReportBatchRunMonitorRead(BaseModel):
    summary: AdminProWeeklyReportBatchRunSummaryRead
    batch_runs: list[ProWeeklyReportBatchRunRead]


class AdminWeeklyReportBatchPreviewRead(BaseModel):
    start_date: date
    end_date: date
    target_merchant_count: int
    would_create_or_update_count: int
    message: str


class ProWeeklyReportDeliveryRunItemRead(BaseModel):
    id: UUID
    delivery_run_id: UUID
    merchant_id: UUID
    snapshot_id: UUID | None = None
    status: str
    reason: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProWeeklyReportDeliveryRunRead(BaseModel):
    id: UUID
    run_type: str
    channel: str
    status: str
    period_start: date
    period_end: date
    total_count: int
    ready_count: int
    skipped_count: int
    failed_count: int
    message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
    items: list[ProWeeklyReportDeliveryRunItemRead]

    model_config = ConfigDict(from_attributes=True)


class AdminProWeeklyReportDeliveryRunHistoryRead(BaseModel):
    delivery_runs: list[ProWeeklyReportDeliveryRunRead]


class ProWeeklyReportInAppNotificationRead(BaseModel):
    notification_id: UUID
    snapshot_id: UUID
    title: str
    message: str
    status: str
    created_at: datetime
    read_at: datetime | None = None


class MerchantProWeeklyReportNotificationListRead(BaseModel):
    notifications: list[ProWeeklyReportInAppNotificationRead]


class AdminProWeeklyReportNotificationSummaryRead(BaseModel):
    total_count: int
    unread_count: int
    read_count: int
    read_rate: float
    latest_created_at: datetime | None = None
    latest_read_at: datetime | None = None


class AdminProWeeklyReportNotificationRead(BaseModel):
    notification_id: UUID
    merchant_id: UUID
    snapshot_id: UUID
    delivery_run_id: UUID
    title: str
    message: str
    status: str
    created_at: datetime
    read_at: datetime | None = None


class AdminProWeeklyReportNotificationListRead(BaseModel):
    notifications: list[AdminProWeeklyReportNotificationRead]


class MerchantProWeeklyReportUnreadCountRead(BaseModel):
    unread_count: int


class MerchantProWeeklyReportReadAllResultRead(BaseModel):
    updated_count: int
    unread_count: int


class AdminProOperationsBatchSummaryRead(BaseModel):
    latest_status: str | None = None
    latest_created_at: datetime | None = None
    latest_run_type: str | None = None
    latest_total_count: int
    latest_success_count: int
    latest_failed_count: int
    latest_skipped_count: int
    recent_7_days_run_count: int
    recent_7_days_failed_or_partial_count: int


class AdminProOperationsDeliverySummaryRead(BaseModel):
    latest_status: str | None = None
    latest_run_type: str | None = None
    latest_channel: str | None = None
    latest_created_at: datetime | None = None
    latest_total_count: int
    latest_ready_count: int
    latest_sent_count: int
    latest_skipped_count: int
    latest_failed_count: int


class AdminProOperationsNotificationSummaryRead(BaseModel):
    total_count: int
    read_count: int
    unread_count: int
    read_rate: float
    latest_created_at: datetime | None = None
    latest_read_at: datetime | None = None
    latest_reminder_at: datetime | None = None
    unread_reminder_count: int


class AdminProOperationsAttentionSummaryRead(BaseModel):
    failed_batch_count: int
    partial_batch_count: int
    failed_delivery_count: int
    unread_notification_count: int
    needs_attention: bool
    attention_messages: list[str]


class AdminProOperationsSummaryRead(BaseModel):
    batch: AdminProOperationsBatchSummaryRead
    delivery: AdminProOperationsDeliverySummaryRead
    notifications: AdminProOperationsNotificationSummaryRead
    attention: AdminProOperationsAttentionSummaryRead
