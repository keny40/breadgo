from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.product import ProductRead


class ProductTemplateCreate(BaseModel):
    source_product_id: UUID
    template_name: str = Field(min_length=1, max_length=255)
    day_of_week: int = Field(ge=0, le=6)
    default_stock_quantity: int = Field(ge=0)
    start_time: time
    end_time: time
    is_active: bool = True

    @model_validator(mode="after")
    def validate_time_range(self) -> "ProductTemplateCreate":
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be earlier than end_time")
        return self


class ProductTemplateUpdate(BaseModel):
    source_product_id: UUID | None = None
    template_name: str | None = Field(default=None, min_length=1, max_length=255)
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    default_stock_quantity: int | None = Field(default=None, ge=0)
    start_time: time | None = None
    end_time: time | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_time_range(self) -> "ProductTemplateUpdate":
        if self.start_time is not None and self.end_time is not None:
            if self.start_time >= self.end_time:
                raise ValueError("start_time must be earlier than end_time")
        return self


class ProductTemplateCreateProductRequest(BaseModel):
    target_date: date | None = None
    stock_quantity: int | None = Field(default=None, ge=0)
    is_visible: bool = True
    name_suffix: str | None = Field(default=None, max_length=80)


class ProductTemplateBatchCreateRequest(BaseModel):
    target_date: date | None = None
    is_visible: bool = True
    name_suffix: str | None = Field(default=None, max_length=80)


class ProductTemplateRead(BaseModel):
    id: UUID
    merchant_id: UUID
    source_product_id: UUID
    template_name: str
    day_of_week: int
    default_stock_quantity: int
    start_time: time
    end_time: time
    is_active: bool
    created_at: datetime
    updated_at: datetime
    source_product_name: str | None = None
    source_store_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductTemplateCreateProductsResponse(BaseModel):
    created_products: list[ProductRead]
    skipped_template_ids: list[UUID]

