from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.pro_dashboard import MerchantProDashboardRead
from app.services.merchant_service import require_merchant_for_user
from app.services.pro_dashboard_service import build_merchant_pro_dashboard

router = APIRouter()


@router.get("/dashboard", response_model=MerchantProDashboardRead)
def get_merchant_pro_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantProDashboardRead:
    merchant = require_merchant_for_user(db, current_user)
    return build_merchant_pro_dashboard(db, merchant)

