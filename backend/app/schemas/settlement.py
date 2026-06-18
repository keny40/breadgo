from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.settlement import SettlementStatus


class SettlementStatusUpdate(BaseModel):
    status: SettlementStatus
    admin_memo: str | None = None
    hold_reason: str | None = None


class SettlementRead(BaseModel):
    id: UUID
    merchant_id: UUID
    store_id: UUID
    reservation_id: UUID
    payment_id: UUID
    gross_amount: Decimal
    platform_fee_rate: Decimal
    platform_fee_amount: Decimal
    pg_fee_rate: Decimal
    pg_fee_amount: Decimal
    merchant_settlement_amount: Decimal
    status: SettlementStatus
    settled_at: datetime | None
    admin_memo: str | None = None
    hold_reason: str | None = None
    created_at: datetime
    updated_at: datetime
    product_name: str | None = None
    store_name: str | None = None
    merchant_name: str | None = None
    merchant_email: str | None = None
    reservation_status: str | None = None
    payment_status: str | None = None
    pickup_code: str | None = None
    bank_name: str | None = None
    bank_account_number: str | None = None
    bank_account_holder: str | None = None
    settlement_cycle: str | None = None
    settlement_memo: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SettlementSummary(BaseModel):
    total_gross_amount: Decimal
    total_platform_fee_amount: Decimal
    total_pg_fee_amount: Decimal
    total_merchant_settlement_amount: Decimal
    pending_amount: Decimal
    ready_amount: Decimal
    paid_amount: Decimal
    hold_amount: Decimal
    cancelled_amount: Decimal
    count_by_status: dict[str, int]
