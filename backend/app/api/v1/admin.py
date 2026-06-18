from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import AdminSummary, DemoSeedResponse, MerchantStatusUpdate
from app.schemas.auth import UserResponse
from app.schemas.merchant import MerchantRead
from app.schemas.payment import PaymentRead
from app.schemas.product import ProductRead
from app.schemas.reservation import DeliveryStatusUpdate, ReservationRead
from app.schemas.store import StoreRead
from app.services.admin_service import (
    get_admin_summary,
    get_merchants,
    get_payments,
    get_products,
    get_reservations,
    get_stores,
    get_users,
    require_admin_user,
    update_merchant_status,
)
from app.services.reservation_service import update_delivery_status_for_admin
from app.api.v1.reservations import reservation_to_read
from scripts.seed_demo import seed_demo_data


router = APIRouter()


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    return require_admin_user(current_user)


@router.get("/summary", response_model=AdminSummary)
def get_summary(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminSummary:
    return get_admin_summary(db)


@router.get("/users", response_model=list[UserResponse])
def list_users(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    return [UserResponse.model_validate(user) for user in get_users(db)]


@router.get("/merchants", response_model=list[MerchantRead])
def list_merchants(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[MerchantRead]:
    return [MerchantRead.model_validate(merchant) for merchant in get_merchants(db)]


@router.get("/stores", response_model=list[StoreRead])
def list_stores(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[StoreRead]:
    return [StoreRead.model_validate(store) for store in get_stores(db)]


@router.get("/products", response_model=list[ProductRead])
def list_products(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[ProductRead]:
    return [ProductRead.model_validate(product) for product in get_products(db)]


@router.get("/reservations", response_model=list[ReservationRead])
def list_reservations(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[ReservationRead]:
    return [ReservationRead.model_validate(reservation) for reservation in get_reservations(db)]


@router.patch("/reservations/{reservation_id}/delivery-status", response_model=ReservationRead)
def change_reservation_delivery_status(
    reservation_id: UUID,
    payload: DeliveryStatusUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ReservationRead:
    reservation = update_delivery_status_for_admin(db, reservation_id, payload)
    return reservation_to_read(reservation)


@router.get("/payments", response_model=list[PaymentRead])
def list_payments(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[PaymentRead]:
    return [PaymentRead.model_validate(payment) for payment in get_payments(db)]


@router.patch("/merchants/{merchant_id}/status", response_model=MerchantRead)
def change_merchant_status(
    merchant_id: UUID,
    payload: MerchantStatusUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> MerchantRead:
    merchant = update_merchant_status(db, merchant_id, payload)
    return MerchantRead.model_validate(merchant)


@router.post("/demo/seed", response_model=DemoSeedResponse)
def seed_demo(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> DemoSeedResponse:
    return DemoSeedResponse(**seed_demo_data(db))
