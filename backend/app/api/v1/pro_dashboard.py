from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.pro_dashboard import MerchantProDashboardRead
from app.schemas.pro_esg import MerchantProEsgReportRead
from app.schemas.pro_recommendation import MerchantProRecommendationsRead
from app.services.merchant_service import require_merchant_for_user
from app.services.pro_dashboard_service import build_merchant_pro_dashboard
from app.services.pro_esg_service import build_merchant_pro_esg_report
from app.services.pro_recommendation_service import build_merchant_pro_recommendations

router = APIRouter()


@router.get("/dashboard", response_model=MerchantProDashboardRead)
def get_merchant_pro_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantProDashboardRead:
    merchant = require_merchant_for_user(db, current_user)
    return build_merchant_pro_dashboard(db, merchant)


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
