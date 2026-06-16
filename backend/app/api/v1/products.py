from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.services.merchant_service import require_merchant_for_user
from app.services.product_service import (
    create_product_for_store,
    get_my_products,
    get_products_by_store,
    hide_product,
    update_product,
)


router = APIRouter()
store_router = APIRouter()


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


@store_router.get("/{store_id}/products", response_model=list[ProductRead])
def get_store_active_products(
    store_id: UUID,
    db: Session = Depends(get_db),
) -> list[ProductRead]:
    return [ProductRead.model_validate(product) for product in get_products_by_store(db, store_id)]
