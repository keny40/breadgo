from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProPlanFeatures(BaseModel):
    yield_dashboard: bool
    relist_products: bool
    product_templates: bool
    csv_product_import: bool
    esg_report: bool
    recommendations: bool
    recommendation_performance: bool
    product_funnel: bool
    multi_store_dashboard: bool


class MerchantProPlanRead(BaseModel):
    merchant_id: UUID
    business_name: str
    current_plan: str
    plan_label: str
    is_pro_active: bool
    trial_ends_at: datetime | None
    features: ProPlanFeatures
    upgrade_message: str
