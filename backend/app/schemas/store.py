from datetime import datetime, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StoreCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1, max_length=500)
    address_detail: str | None = Field(default=None, max_length=255)
    sido: str | None = Field(default=None, max_length=100)
    sigungu: str | None = Field(default=None, max_length=100)
    dong: str | None = Field(default=None, max_length=100)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90, max_digits=9, decimal_places=6)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180, max_digits=9, decimal_places=6)
    phone_number: str = Field(min_length=1, max_length=32)
    description: str | None = None
    opening_time: time
    closing_time: time

    @model_validator(mode="after")
    def validate_hours(self) -> "StoreCreate":
        if self.opening_time >= self.closing_time:
            raise ValueError("opening_time must be earlier than closing_time")
        return self


class StoreUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, min_length=1, max_length=500)
    address_detail: str | None = Field(default=None, max_length=255)
    sido: str | None = Field(default=None, max_length=100)
    sigungu: str | None = Field(default=None, max_length=100)
    dong: str | None = Field(default=None, max_length=100)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90, max_digits=9, decimal_places=6)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180, max_digits=9, decimal_places=6)
    phone_number: str | None = Field(default=None, min_length=1, max_length=32)
    description: str | None = None
    opening_time: time | None = None
    closing_time: time | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_hours(self) -> "StoreUpdate":
        if (
            self.opening_time is not None
            and self.closing_time is not None
            and self.opening_time >= self.closing_time
        ):
            raise ValueError("opening_time must be earlier than closing_time")
        return self


class StoreRead(BaseModel):
    id: UUID
    merchant_id: UUID
    name: str
    address: str
    address_detail: str | None
    sido: str | None
    sigungu: str | None
    dong: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    phone_number: str
    description: str | None
    opening_time: time
    closing_time: time
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
