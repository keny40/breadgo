from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


ProductEventType = Literal["LIST_VIEW", "DETAIL_VIEW", "RESERVATION_STARTED", "RESERVATION_CREATED"]
ProductEventSource = Literal["WEB", "MOBILE"]


class ProductEventCreate(BaseModel):
    event_type: ProductEventType
    source: ProductEventSource = "WEB"


class ProductEventRead(BaseModel):
    id: UUID
    product_id: UUID
    store_id: UUID | None
    merchant_id: UUID | None
    user_id: UUID | None
    event_type: str
    source: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
