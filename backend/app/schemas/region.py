from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.product import ProductStatus


class RegionProductRead(BaseModel):
    id: UUID
    store_id: UUID
    store_name: str
    store_address: str
    sido: str | None
    sigungu: str | None
    dong: str | None
    name: str
    description: str | None
    original_price: Decimal
    discount_price: Decimal
    quantity: int
    pickup_start_time: datetime
    pickup_end_time: datetime
    status: ProductStatus

    model_config = ConfigDict(from_attributes=True)
