from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProInventoryAlertRead(BaseModel):
    product_id: UUID
    product_name: str
    store_id: UUID
    store_name: str
    severity: str
    alert_type: str
    title: str
    message: str
    suggested_action: str
    current_stock_quantity: int
    related_metric: str | None = None
    recent_inventory_note: str | None = None
    detected_at: datetime
    latest_action_type: str | None = None
    latest_action_at: datetime | None = None
    is_acknowledged: bool = False
    is_resolved: bool = False


class MerchantProInventoryAlertsRead(BaseModel):
    total_alerts: int
    high_count: int
    medium_count: int
    low_count: int
    alerts: list[ProInventoryAlertRead]
