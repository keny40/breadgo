from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ProRecommendationRead(BaseModel):
    product_id: UUID
    product_name: str
    store_id: UUID
    store_name: str
    recent_reserved_quantity: int
    recent_picked_up_quantity: int
    recent_cancelled_quantity: int
    current_stock_quantity: int
    sell_through_rate: float
    pickup_completion_rate: float
    recommended_stock_quantity: int
    current_discount_price: Decimal
    recommended_discount_price: Decimal
    recommendation_type: str
    recommendation_message: str
    confidence_label: str


class MerchantProRecommendationsRead(BaseModel):
    period_days: int
    note: str
    recommendations: list[ProRecommendationRead]

