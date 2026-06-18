from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.payment import PaymentMethod, PaymentStatus


class PaymentReadyRequest(BaseModel):
    reservation_id: UUID
    method: PaymentMethod


class PaymentConfirmRequest(BaseModel):
    payment_id: UUID


class PaymentFailRequest(BaseModel):
    payment_id: UUID


class PaymentCancelRequest(BaseModel):
    payment_id: UUID


class PaymentRead(BaseModel):
    id: UUID
    reservation_id: UUID
    user_id: UUID
    amount: Decimal
    method: PaymentMethod
    provider: str
    status: PaymentStatus
    paid_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime
    product_name: str | None = None
    store_name: str | None = None
    reservation_status: str | None = None
    pickup_code: str | None = None
    fulfillment_method: str | None = None
    delivery_fee: Decimal | None = None
    delivery_status: str | None = None

    model_config = ConfigDict(from_attributes=True)
