from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.product import ProductStatus


class ProductCreate(BaseModel):
    store_id: UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    original_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    discount_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    quantity: int = Field(ge=0)
    pickup_start_time: datetime
    pickup_end_time: datetime
    status: ProductStatus = ProductStatus.ACTIVE

    @model_validator(mode="after")
    def validate_product(self) -> "ProductCreate":
        if self.discount_price > self.original_price:
            raise ValueError("discount_price cannot be greater than original_price")
        if self.pickup_start_time >= self.pickup_end_time:
            raise ValueError("pickup_start_time must be earlier than pickup_end_time")
        return self


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    original_price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    discount_price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    quantity: int | None = Field(default=None, ge=0)
    pickup_start_time: datetime | None = None
    pickup_end_time: datetime | None = None
    status: ProductStatus | None = None

    @model_validator(mode="after")
    def validate_product(self) -> "ProductUpdate":
        if (
            self.original_price is not None
            and self.discount_price is not None
            and self.discount_price > self.original_price
        ):
            raise ValueError("discount_price cannot be greater than original_price")
        if (
            self.pickup_start_time is not None
            and self.pickup_end_time is not None
            and self.pickup_start_time >= self.pickup_end_time
        ):
            raise ValueError("pickup_start_time must be earlier than pickup_end_time")
        return self


class ProductRead(BaseModel):
    id: UUID
    store_id: UUID
    name: str
    description: str | None
    original_price: Decimal
    discount_price: Decimal
    quantity: int
    pickup_start_time: datetime
    pickup_end_time: datetime
    status: ProductStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
