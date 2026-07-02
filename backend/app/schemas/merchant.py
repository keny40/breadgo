from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.merchant import MerchantPlan, MerchantStatus


class MerchantCreate(BaseModel):
    business_name: str = Field(min_length=1, max_length=255)
    business_registration_number: str = Field(min_length=1, max_length=64)
    representative_name: str = Field(min_length=1, max_length=255)
    phone_number: str = Field(min_length=1, max_length=32)


class MerchantRead(BaseModel):
    id: UUID
    user_id: UUID
    business_name: str
    business_registration_number: str
    representative_name: str
    phone_number: str
    status: MerchantStatus
    status_reason: str | None = None
    plan: MerchantPlan = MerchantPlan.FREE
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MerchantMeResponse(BaseModel):
    merchant: MerchantRead
