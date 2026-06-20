from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.product import ProductStatus


class ProductCreate(BaseModel):
    store_id: UUID
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=1000)
    original_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    discount_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    quantity: int = Field(ge=0)
    allow_pickup: bool = True
    allow_quick_delivery: bool = False
    allow_parcel_delivery: bool = False
    quick_delivery_fee: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)
    parcel_delivery_fee: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)
    pickup_start_time: datetime
    pickup_end_time: datetime
    status: ProductStatus = ProductStatus.ACTIVE

    @model_validator(mode="after")
    def validate_product(self) -> "ProductCreate":
        if self.discount_price > self.original_price:
            raise ValueError("discount_price cannot be greater than original_price")
        if self.pickup_start_time >= self.pickup_end_time:
            raise ValueError("pickup_start_time must be earlier than pickup_end_time")
        if not (self.allow_pickup or self.allow_quick_delivery or self.allow_parcel_delivery):
            raise ValueError("at least one fulfillment method must be allowed")
        return self


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=1000)
    original_price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    discount_price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    quantity: int | None = Field(default=None, ge=0)
    allow_pickup: bool | None = None
    allow_quick_delivery: bool | None = None
    allow_parcel_delivery: bool | None = None
    quick_delivery_fee: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    parcel_delivery_fee: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
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


class ProductDuplicateCreate(BaseModel):
    stock_quantity: int | None = Field(default=None, ge=0)
    sale_starts_at: datetime | None = None
    sale_ends_at: datetime | None = None
    is_visible: bool = True
    name_suffix: str | None = Field(default=None, max_length=80)

    @model_validator(mode="after")
    def validate_duplicate_product(self) -> "ProductDuplicateCreate":
        if self.sale_starts_at is not None and self.sale_ends_at is not None:
            if self.sale_starts_at >= self.sale_ends_at:
                raise ValueError("sale_starts_at must be earlier than sale_ends_at")
        return self


class ProductCsvImportError(BaseModel):
    row_number: int
    field: str
    message: str


class ProductCsvImportResult(BaseModel):
    total_rows: int
    success_count: int
    failed_count: int
    created_product_ids: list[UUID]
    errors: list[ProductCsvImportError]


class ProductRead(BaseModel):
    id: UUID
    store_id: UUID
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
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
