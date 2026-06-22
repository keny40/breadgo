from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.pro_dashboard import MerchantProDashboardRead, MerchantProStoresDashboardRead
from app.schemas.pro_esg import MerchantProEsgReportRead
from app.schemas.pro_inventory_alert import MerchantProInventoryAlertsRead
from app.schemas.pro_plan import MerchantProPlanRead
from app.schemas.pro_product_funnel import MerchantProProductFunnelRead
from app.schemas.product_inventory_event import ProductInventoryEventRead
from app.schemas.pro_recommendation import (
    MerchantProRecommendationPerformanceRead,
    MerchantProRecommendationsRead,
    ProRecommendationDraftCreateRequest,
    ProRecommendationDraftCreateResponse,
)
from app.schemas.pos_integration import (
    MockPosSyncRequest,
    MockPosSyncResult,
    PosIntegrationRead,
    PosIntegrationUpsert,
    PosSyncBatchRead,
)
from app.schemas.recommendation_action_event import RecommendationActionEventCreate, RecommendationActionEventRead
from app.services.merchant_service import require_merchant_for_user
from app.services.pos_integration_service import (
    get_pos_sync_batch,
    get_pos_sync_batches,
    read_pos_integration,
    run_mock_pos_sync,
    upsert_pos_integration,
)
from app.services.product_inventory_event_service import list_inventory_events
from app.services.pro_dashboard_service import build_merchant_pro_dashboard, build_merchant_pro_stores_dashboard
from app.services.pro_esg_service import build_merchant_pro_esg_report
from app.services.pro_inventory_alert_service import build_merchant_pro_inventory_alerts
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


@router.get("/inventory-events", response_model=list[ProductInventoryEventRead])
def get_merchant_pro_inventory_events(
    product_id: UUID | None = None,
    event_type: str | None = None,
    source_type: str | None = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProductInventoryEventRead]:
    merchant = require_merchant_for_user(db, current_user)
    return list_inventory_events(
        db,
        merchant,
        product_id=product_id,
        event_type=event_type,
        source_type=source_type,
        limit=limit,
    )


@router.get("/inventory-alerts", response_model=MerchantProInventoryAlertsRead)
def get_merchant_pro_inventory_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantProInventoryAlertsRead:
    merchant = require_merchant_for_user(db, current_user)
    return build_merchant_pro_inventory_alerts(db, merchant)


@router.get("/pos-integration", response_model=PosIntegrationRead)
def get_merchant_pro_pos_integration(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PosIntegrationRead:
    merchant = require_merchant_for_user(db, current_user)
    return read_pos_integration(db, merchant)


@router.post("/pos-integration", response_model=PosIntegrationRead)
def save_merchant_pro_pos_integration(
    payload: PosIntegrationUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PosIntegrationRead:
    merchant = require_merchant_for_user(db, current_user)
    integration = upsert_pos_integration(db, merchant, payload)
    return PosIntegrationRead.model_validate(integration)


@router.post("/pos-integration/mock-sync", response_model=MockPosSyncResult)
def run_merchant_pro_mock_pos_sync(
    payload: MockPosSyncRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MockPosSyncResult:
    merchant = require_merchant_for_user(db, current_user)
    return run_mock_pos_sync(db, merchant, payload)


@router.get("/pos-integration/sync-batches", response_model=list[PosSyncBatchRead])
def get_merchant_pro_pos_sync_batches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PosSyncBatchRead]:
    merchant = require_merchant_for_user(db, current_user)
    return get_pos_sync_batches(db, merchant)


@router.get("/pos-integration/sync-batches/{batch_id}", response_model=PosSyncBatchRead)
def get_merchant_pro_pos_sync_batch(
    batch_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PosSyncBatchRead:
    merchant = require_merchant_for_user(db, current_user)
    return get_pos_sync_batch(db, merchant, batch_id)
