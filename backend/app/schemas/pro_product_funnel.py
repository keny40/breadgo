from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class ProProductFunnelSummary(BaseModel):
    product_id: UUID
    product_name: str
    store_id: UUID
    store_name: str
    detail_views: int
    reservation_started_count: int
    reservations: int
    paid_count: int
    picked_up_count: int
    conversion_rate: float
    paid_conversion_rate: float
    pickup_conversion_rate: float
    paid_amount: Decimal
    from_recommendation: bool
    attention_label: str


class MerchantProProductFunnelRead(BaseModel):
    period_days: int
    total_detail_views: int
    total_reservation_starts: int
    total_reservations: int
    total_paid_count: int
    total_picked_up_count: int
    detail_to_reservation_rate: float
    product_funnel_summaries: list[ProProductFunnelSummary]
