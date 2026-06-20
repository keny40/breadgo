from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PosIntegrationUpsert(BaseModel):
    provider: str = Field(default="MOCK_POS")
    store_id: UUID | None = None
    external_store_code: str | None = Field(default=None, max_length=120)


class PosIntegrationRead(BaseModel):
    id: UUID
    merchant_id: UUID
    store_id: UUID | None
    provider: str
    status: str
    external_store_code: str | None
    last_synced_at: datetime | None
    last_sync_status: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MockPosItem(BaseModel):
    external_sku: str = Field(min_length=1, max_length=120)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    original_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    discount_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock_quantity: int = Field(ge=0)
    sale_starts_at: datetime
    sale_ends_at: datetime
    pickup_available: bool = True
    quick_delivery_available: bool = False
    parcel_delivery_available: bool = False
    quick_delivery_fee: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)
    parcel_delivery_fee: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2)

    @model_validator(mode="after")
    def validate_item(self) -> "MockPosItem":
        if self.discount_price > self.original_price:
            raise ValueError("discount_price cannot be greater than original_price")
        if self.sale_starts_at >= self.sale_ends_at:
            raise ValueError("sale_starts_at must be earlier than sale_ends_at")
        if not (self.pickup_available or self.quick_delivery_available or self.parcel_delivery_available):
            raise ValueError("at least one fulfillment method must be available")
        return self


class MockPosSyncRequest(BaseModel):
    mock_items: list[MockPosItem] = Field(min_length=1, max_length=200)


class PosSyncRowRead(BaseModel):
    id: UUID
    batch_id: UUID
    external_sku: str | None
    product_id: UUID | None
    action: str
    product_name: str | None
    error_message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PosSyncBatchRead(BaseModel):
    id: UUID
    integration_id: UUID
    merchant_id: UUID
    store_id: UUID | None
    total_rows: int
    created_count: int
    updated_count: int
    skipped_count: int
    failed_count: int
    status: str
    created_at: datetime
    rows: list[PosSyncRowRead] = []

    model_config = ConfigDict(from_attributes=True)


class MockPosSyncResult(BaseModel):
    batch_id: UUID
    total_rows: int
    created_count: int
    updated_count: int
    skipped_count: int
    failed_count: int
    status: str
    rows: list[PosSyncRowRead]
