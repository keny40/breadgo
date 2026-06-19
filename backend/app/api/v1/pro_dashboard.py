from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.pro_dashboard import MerchantProDashboardRead, MerchantProStoresDashboardRead
from app.schemas.pro_esg import MerchantProEsgReportRead
from app.schemas.pro_plan import MerchantProPlanRead
from app.schemas.pro_product_funnel import MerchantProProductFunnelRead
from app.schemas.pro_recommendation import (
    MerchantProRecommendationPerformanceRead,
    MerchantProRecommendationsRead,
    ProRecommendationDraftCreateRequest,
    ProRecommendationDraftCreateResponse,
)
from app.schemas.recommendation_action_event import RecommendationActionEventCreate, RecommendationActionEventRead
from app.services.merchant_service import require_merchant_for_user
from app.services.pro_dashboard_service import build_merchant_pro_dashboard, build_merchant_pro_stores_dashboard
from app.services.pro_esg_service import build_merchant_pro_esg_report
from app.services.pro_plan_service import build_merchant_pro_plan
from app.services.pro_product_funnel_service import build_merchant_pro_product_funnel
from app.services.pro_recommendation_service import (
    build_merchant_pro_recommendation_performance,
    build_merchant_pro_recommendations,
    create_recommendation_draft,
)
from app.services.recommendation_action_event_service import record_recommendation_action_event

router = APIRouter()


@router.get("/dashboard", response_model=MerchantProDashboardRead)
def get_merchant_pro_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantProDashboardRead:
    merchant = require_merchant_for_user(db, current_user)
    return build_merchant_pro_dashboard(db, merchant)


@router.get("/plan", response_model=MerchantProPlanRead)
def get_merchant_pro_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantProPlanRead:
    merchant = require_merchant_for_user(db, current_user)
    return build_merchant_pro_plan(merchant)


@router.get("/stores-dashboard", response_model=MerchantProStoresDashboardRead)
def get_merchant_pro_stores_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantProStoresDashboardRead:
    merchant = require_merchant_for_user(db, current_user)
    return build_merchant_pro_stores_dashboard(db, merchant)


@router.get("/esg-report", response_model=MerchantProEsgReportRead)
def get_merchant_pro_esg_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantProEsgReportRead:
    merchant = require_merchant_for_user(db, current_user)
    return build_merchant_pro_esg_report(db, merchant)


@router.get("/recommendations", response_model=MerchantProRecommendationsRead)
def get_merchant_pro_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantProRecommendationsRead:
    merchant = require_merchant_for_user(db, current_user)
    return build_merchant_pro_recommendations(db, merchant)


@router.post("/recommendations/{product_id}/create-draft", response_model=ProRecommendationDraftCreateResponse)
def create_merchant_pro_recommendation_draft(
    product_id: UUID,
    payload: ProRecommendationDraftCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProRecommendationDraftCreateResponse:
    merchant = require_merchant_for_user(db, current_user)
    return create_recommendation_draft(db, merchant, product_id, payload)


@router.post("/recommendation-action-events", response_model=RecommendationActionEventRead)
def create_merchant_pro_recommendation_action_event(
    payload: RecommendationActionEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecommendationActionEventRead:
    merchant = require_merchant_for_user(db, current_user)
    event = record_recommendation_action_event(db, merchant, payload)
    return RecommendationActionEventRead.model_validate(event)


@router.get("/recommendation-performance", response_model=MerchantProRecommendationPerformanceRead)
def get_merchant_pro_recommendation_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantProRecommendationPerformanceRead:
    merchant = require_merchant_for_user(db, current_user)
    return build_merchant_pro_recommendation_performance(db, merchant)


@router.get("/product-funnel", response_model=MerchantProProductFunnelRead)
def get_merchant_pro_product_funnel(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantProProductFunnelRead:
    merchant = require_merchant_for_user(db, current_user)
    return build_merchant_pro_product_funnel(db, merchant)
