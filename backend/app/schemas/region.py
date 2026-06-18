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
    distance_km: float | None = None
    name: str
    description: str | None
    image_url: str | None
    original_price: Decimal
    discount_price: Decimal
    quantity: int
    allow_pickup: bool
    allow_quick_delivery: bool
    allow_parcel_delivery: bool
    quick_delivery_fee: Decimal
    parcel_delivery_fee: Decimal
    pickup_start_time: datetime
    pickup_end_time: datetime
    status: ProductStatus

    model_config = ConfigDict(from_attributes=True)
