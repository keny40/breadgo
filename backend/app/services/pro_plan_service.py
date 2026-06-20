from app.models.merchant import Merchant
from app.schemas.pro_plan import MerchantProPlanRead, ProPlanFeatures


DEFAULT_MERCHANT_PRO_PLAN = "PRO"


PLAN_LABELS = {
    "FREE": "Free",
    "PRO": "BreadGo Pro",
    "ENTERPRISE": "BreadGo Enterprise",
}


PLAN_FEATURES = {
    "FREE": ProPlanFeatures(
        yield_dashboard=False,
        relist_products=False,
        product_templates=False,
        csv_product_import=False,
        esg_report=False,
        recommendations=False,
        recommendation_performance=False,
        product_funnel=False,
        multi_store_dashboard=False,
        pos_api_integration=False,
    ),
    "PRO": ProPlanFeatures(
        yield_dashboard=True,
        relist_products=True,
        product_templates=True,
        csv_product_import=True,
        esg_report=True,
        recommendations=True,
        recommendation_performance=True,
        product_funnel=True,
        multi_store_dashboard=False,
        pos_api_integration=False,
    ),
    "ENTERPRISE": ProPlanFeatures(
        yield_dashboard=True,
        relist_products=True,
        product_templates=True,
        csv_product_import=True,
        esg_report=True,
        recommendations=True,
        recommendation_performance=True,
        product_funnel=True,
        multi_store_dashboard=True,
        pos_api_integration=True,
    ),
}


def build_merchant_pro_plan(merchant: Merchant) -> MerchantProPlanRead:
    current_plan = DEFAULT_MERCHANT_PRO_PLAN
    features = PLAN_FEATURES[current_plan]
    upgrade_message = (
        "추천, ESG, 고객 전환 분석은 BreadGo Pro 기능입니다. "
        "다중 매장 통합, 프랜차이즈 리포트, POS/API 연동은 Enterprise 확장 기능으로 준비 중입니다. "
        "현재는 실제 과금 연동 없이 MVP 플랜 안내만 제공합니다."
    )

    return MerchantProPlanRead(
        merchant_id=merchant.id,
        business_name=merchant.business_name,
        current_plan=current_plan,
        plan_label=PLAN_LABELS[current_plan],
        is_pro_active=current_plan in {"PRO", "ENTERPRISE"},
        trial_ends_at=None,
        features=features,
        upgrade_message=upgrade_message,
    )
