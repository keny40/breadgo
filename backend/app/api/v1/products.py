from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.api.v1.auth import bearer_scheme, get_current_user
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.product_event import ProductEventCreate, ProductEventRead
from app.schemas.product import ProductCreate, ProductDuplicateCreate, ProductRead, ProductUpdate
from app.services.merchant_service import require_merchant_for_user
from app.services.product_service import (
    create_product_for_store,
    duplicate_product_for_merchant,
    get_my_products,
    get_products_by_store,
    hide_product,
    update_product,
)
from app.services.product_event_service import record_product_event


router = APIRouter()
store_router = APIRouter()
merchant_router = APIRouter()


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    if credentials is None:
        return None
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        return None
    try:
        parsed_user_id = UUID(user_id)
    except ValueError:
        return None
    user = db.get(User, parsed_user_id)
    if user is None or not user.is_active:
        return None
    return user


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProductRead:
    merchant = require_merchant_for_user(db, current_user)
    product = create_product_for_store(db, merchant, payload)
    return ProductRead.model_validate(product)


@router.get("/me", response_model=list[ProductRead])
def get_current_merchant_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProductRead]:
    merchant = require_merchant_for_user(db, current_user)
    return [ProductRead.model_validate(product) for product in get_my_products(db, merchant)]


@router.patch("/{product_id}", response_model=ProductRead)
def update_current_merchant_product(
    product_id: UUID,
    payload: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProductRead:
    merchant = require_merchant_for_user(db, current_user)
    product = update_product(db, merchant, product_id, payload)
    return ProductRead.model_validate(product)


@router.delete("/{product_id}", response_model=ProductRead)
def delete_current_merchant_product(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProductRead:
    merchant = require_merchant_for_user(db, current_user)
    product = hide_product(db, merchant, product_id)
    return ProductRead.model_validate(product)


@router.post("/{product_id}/events", response_model=ProductEventRead, status_code=status.HTTP_201_CREATED)
def create_product_event(
    product_id: UUID,
    payload: ProductEventCreate,
    current_user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> ProductEventRead:
    event = record_product_event(db, product_id, payload, current_user)
    return ProductEventRead.model_validate(event)


@merchant_router.post("/{product_id}/duplicate", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def duplicate_current_merchant_product(
    product_id: UUID,
    payload: ProductDuplicateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProductRead:
    merchant = require_merchant_for_user(db, current_user)
    product = duplicate_product_for_merchant(db, merchant, product_id, payload)
    return ProductRead.model_validate(product)


@store_router.get("/{store_id}/products", response_model=list[ProductRead])
def get_store_active_products(
    store_id: UUID,
    db: Session = Depends(get_db),
) -> list[ProductRead]:
    return [ProductRead.model_validate(product) for product in get_products_by_store(db, store_id)]
