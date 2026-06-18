from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SettlementAccountUpdate(BaseModel):
    bank_name: str | None = None
    bank_account_number: str | None = None
    bank_account_holder: str | None = None
    settlement_cycle: str | None = None
    settlement_memo: str | None = None


class SettlementAccountRead(BaseModel):
    merchant_id: UUID
    business_name: str
    bank_name: str | None = None
    bank_account_number: str | None = None
    bank_account_holder: str | None = None
    settlement_cycle: str | None = None
    settlement_memo: str | None = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
