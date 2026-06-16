from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.store import StoreCreate, StoreRead, StoreUpdate
from app.services.merchant_service import (
    create_store_for_merchant,
    get_active_stores,
    get_stores_by_merchant,
    require_merchant_for_user,
    update_store,
)


router = APIRouter()


@router.get("", response_model=list[StoreRead])
def get_public_stores(db: Session = Depends(get_db)) -> list[StoreRead]:
    return [StoreRead.model_validate(store) for store in get_active_stores(db)]


@router.post("", response_model=StoreRead, status_code=status.HTTP_201_CREATED)
def create_store(
    payload: StoreCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StoreRead:
    merchant = require_merchant_for_user(db, current_user)
    store = create_store_for_merchant(db, merchant, payload)
    return StoreRead.model_validate(store)


@router.get("/me", response_model=list[StoreRead])
def get_my_stores(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[StoreRead]:
    merchant = require_merchant_for_user(db, current_user)
    return [StoreRead.model_validate(store) for store in get_stores_by_merchant(db, merchant)]


@router.patch("/{store_id}", response_model=StoreRead)
def update_my_store(
    store_id: UUID,
    payload: StoreUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StoreRead:
    merchant = require_merchant_for_user(db, current_user)
    store = update_store(db, merchant, store_id, payload)
    return StoreRead.model_validate(store)
