from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ProEsgProductSummary(BaseModel):
    product_id: UUID
    product_name: str
    store_id: UUID
    store_name: str
    saved_items: int
    saved_amount: Decimal
    pickup_completed_count: int
    cancelled_count: int
    contribution_rate: float


class ProEsgDailyTrend(BaseModel):
    date: date
    saved_items: int
    saved_amount: Decimal
    pickup_completed_count: int
    cancelled_count: int


class MerchantProEsgReportRead(BaseModel):
    merchant_id: UUID
    business_name: str
    today_saved_items: int
    week_saved_items: int
    month_saved_items: int
    today_saved_amount: Decimal
    week_saved_amount: Decimal
    month_saved_amount: Decimal
    estimated_waste_reduction_items: int
    estimated_waste_prevention_amount: Decimal
    pickup_completed_count: int
    cancelled_count: int
    sell_through_rate: float
    carbon_reduction_note: str
    product_esg_summaries: list[ProEsgProductSummary]
    daily_esg_trend: list[ProEsgDailyTrend]

