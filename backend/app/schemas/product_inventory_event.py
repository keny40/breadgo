from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProductInventoryEventRead(BaseModel):
    id: UUID
    merchant_id: UUID
    store_id: UUID | None
    product_id: UUID
    product_name: str | None
    store_name: str | None
    event_type: str
    quantity_before: int | None
    quantity_after: int | None
    quantity_delta: int | None
    source_type: str | None
    source_id: UUID | None
    note: str | None
    created_at: datetime
