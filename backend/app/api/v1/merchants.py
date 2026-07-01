from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.merchant import MerchantCreate, MerchantMeResponse, MerchantRead
from app.schemas.merchant_application import MerchantApplicationCreate, MerchantApplicationRead
from app.services.merchant_application_service import create_merchant_application
from app.services.merchant_service import create_merchant_for_user, get_merchant_by_user


router = APIRouter()


@router.post("/register", response_model=MerchantRead, status_code=status.HTTP_201_CREATED)
def register_merchant(
    payload: MerchantCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantRead:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Merchant registration requires an application and admin approval.",
    )


@router.post("/apply", response_model=MerchantApplicationRead, status_code=status.HTTP_201_CREATED)
def apply_merchant(
    payload: MerchantApplicationCreate,
    db: Session = Depends(get_db),
) -> MerchantApplicationRead:
    application = create_merchant_application(db, payload)
    return MerchantApplicationRead.model_validate(application)


@router.get("/me", response_model=MerchantMeResponse)
def get_my_merchant(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MerchantMeResponse:
    merchant = get_merchant_by_user(db, current_user)
    if merchant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant profile not found.")
    return MerchantMeResponse(merchant=MerchantRead.model_validate(merchant))
