from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ProProductSummary(BaseModel):
    product_id: UUID
    product_name: str
    store_id: UUID
    store_name: str
    status: str
    registered_quantity: int
    reserved_quantity: int
    paid_quantity: int
    picked_up_quantity: int
    cancelled_quantity: int
    remaining_quantity: int
    gross_sales: Decimal
    estimated_settlement: Decimal
    sell_through_rate: float


class ProDailySummary(BaseModel):
    date: date
    registered_quantity: int
    reserved_quantity: int
    picked_up_quantity: int
    cancelled_count: int
    remaining_quantity: int
    gross_sales: Decimal
    estimated_settlement: Decimal
    sell_through_rate: float


class MerchantProDashboardRead(BaseModel):
    merchant_id: UUID
    business_name: str
    today_registered_quantity: int
    today_reserved_quantity: int
    today_paid_count: int
    today_picked_up_count: int
    today_cancelled_count: int
    today_remaining_quantity: int
    today_gross_sales: Decimal
    today_estimated_settlement: Decimal
    today_estimated_saved_items: int
    today_estimated_waste_prevented_amount: Decimal
    sell_through_rate: float
    pickup_completion_rate: float
    cancellation_rate: float
    product_summaries: list[ProProductSummary]
    recent_7_days: list[ProDailySummary]

