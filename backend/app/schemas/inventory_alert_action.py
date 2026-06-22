from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class InventoryAlertActionCreate(BaseModel):
    product_id: UUID | None = None
    alert_type: str = Field(min_length=1, max_length=80)
    severity: str = Field(min_length=1, max_length=20)
    action_type: str = Field(min_length=1, max_length=40)
    note: str | None = Field(default=None, max_length=1000)


class InventoryAlertActionRead(BaseModel):
    id: UUID
    merchant_id: UUID
    product_id: UUID | None
    product_name: str | None
    alert_type: str
    severity: str
    action_type: str
    note: str | None
    created_at: datetime
