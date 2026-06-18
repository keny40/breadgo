from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ops import OpsStatusResponse
from app.services.admin_service import require_admin_user
from app.services.ops.status_service import build_ops_status


router = APIRouter()


@router.get("/status", response_model=OpsStatusResponse)
def get_ops_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OpsStatusResponse:
    require_admin_user(current_user)
    return build_ops_status(db)
