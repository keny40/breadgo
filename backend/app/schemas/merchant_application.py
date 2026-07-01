from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.merchant_application import MerchantApplicationStatus
from app.schemas.merchant import MerchantRead


class MerchantApplicationCreate(BaseModel):
    store_name: str = Field(min_length=1, max_length=255)
    owner_name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=3, max_length=255)
    phone: str = Field(min_length=1, max_length=32)
    business_registration_number: str = Field(min_length=1, max_length=64)
    address: str = Field(min_length=1, max_length=500)
    region_sido: str | None = Field(default=None, max_length=100)
    region_sigungu: str | None = Field(default=None, max_length=100)
    region_dong: str | None = Field(default=None, max_length=100)
    product_category: str | None = Field(default=None, max_length=100)
    pickup_available_time: str | None = Field(default=None, max_length=100)
    note: str | None = Field(default=None, max_length=2000)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        email = value.strip().lower()
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("email must contain a valid @ address")
        return email


class MerchantApplicationRejectRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class MerchantApplicationRead(BaseModel):
    id: UUID
    store_name: str
    owner_name: str
    email: str
    phone: str
    business_registration_number: str
    address: str
    region_sido: str | None
    region_sigungu: str | None
    region_dong: str | None
    product_category: str | None
    pickup_available_time: str | None
    note: str | None
    status: MerchantApplicationStatus
    rejection_reason: str | None
    reviewed_at: datetime | None
    reviewed_by_user_id: UUID | None
    merchant_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MerchantApplicationApproveResponse(BaseModel):
    application: MerchantApplicationRead
    merchant: MerchantRead
