from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.reservation import ReservationStatus


class ReservationCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1)


class ReservationRead(BaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    store_id: UUID
    quantity: int
    total_price: Decimal
    status: ReservationStatus
    pickup_code: str
    reserved_at: datetime
    pickup_deadline: datetime
    created_at: datetime
    updated_at: datetime
    product_name: str | None = None
    store_name: str | None = None
    customer_email: str | None = None
    customer_name: str | None = None
    payment_status: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ReservationStatusUpdate(BaseModel):
    status: ReservationStatus


class PickupConfirmRequest(BaseModel):
    pickup_code: str = Field(min_length=6, max_length=6)


class PickupConfirmResponse(BaseModel):
    reservation: ReservationRead
