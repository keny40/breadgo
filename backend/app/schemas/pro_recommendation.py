from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.schemas.product import ProductRead


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


class ProRecommendationDraftCreateRequest(BaseModel):
    is_visible: bool = False
    name_suffix: str | None = "추천"


class ProRecommendationDraftCreateResponse(BaseModel):
    created_product: ProductRead
    usage_id: UUID
    recommendation: ProRecommendationRead


class RecommendationTypeUsageSummary(BaseModel):
    recommendation_type: str
    count: int
    picked_up_quantity: int
    paid_amount: Decimal


class RecommendationUsageRead(BaseModel):
    id: UUID
    source_product_id: UUID
    source_product_name: str | None = None
    created_product_id: UUID | None
    created_product_name: str | None = None
    recommendation_type: str
    confidence_label: str
    recommended_stock_quantity: int
    recommended_discount_price: Decimal
    original_stock_quantity: int | None = None
    original_discount_price: Decimal | None = None
    action_type: str
    created_product_reserved_quantity: int
    created_product_picked_up_quantity: int
    created_product_paid_amount: Decimal
    created_product_sell_through_rate: float
    created_at: str


class MerchantProRecommendationPerformanceRead(BaseModel):
    total_recommendation_drafts: int
    used_recommendation_count: int
    recommendation_created_products_count: int
    picked_up_quantity_from_recommendations: int
    paid_amount_from_recommendations: Decimal
    average_sell_through_rate_from_recommendations: float
    usage_by_recommendation_type: list[RecommendationTypeUsageSummary]
    recent_usages: list[RecommendationUsageRead]
