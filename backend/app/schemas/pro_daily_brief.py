from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


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
