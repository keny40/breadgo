from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.reservation import Reservation
from app.models.reservation_history import ReservationHistory
from app.schemas.reservation_history import ReservationHistoryRead
from app.models.user import User
from app.schemas.reservation import (
    PickupConfirmRequest,
    PickupConfirmResponse,
    DeliveryStatusUpdate,
    ReservationCreate,
    ReservationRead,
    ReservationStatusUpdate,
)
from app.services.merchant_service import require_merchant_for_user
from app.services.reservation_service import (
    cancel_reservation,
    confirm_pickup_by_code,
    create_reservation,
    get_my_reservations,
    get_reservations_for_merchant,
    get_reservation_by_pickup_code_for_merchant,
    get_store_reservations_for_merchant,
    update_reservation_status,
    update_delivery_status_for_merchant,
)
from app.services.reservation_history_service import (
    get_history_for_customer,
    get_history_for_merchant,
)


router = APIRouter()
store_router = APIRouter()
merchant_router = APIRouter()


def reservation_to_read(reservation: Reservation) -> ReservationRead:
    payload = ReservationRead.model_validate(reservation)
    payload.product_name = reservation.product.name if reservation.product else None
    payload.store_name = reservation.store.name if reservation.store else None
    payload.customer_email = reservation.user.email if reservation.user else None
    payload.customer_name = reservation.user.full_name if reservation.user else None
    if reservation.payment:
        payload.payment_status = reservation.payment.status.value
    return payload


def reservation_history_to_read(event: ReservationHistory) -> ReservationHistoryRead:
    payload = ReservationHistoryRead.model_validate(event)
    payload.actor_email = event.actor.email if event.actor else None
    return payload


@router.post("", response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
def create_current_user_reservation(
    payload: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReservationRead:
    reservation = create_reservation(db, current_user, payload)
    return reservation_to_read(reservation)


@router.get("/me", response_model=list[ReservationRead])
def get_current_user_reservations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ReservationRead]:
    return [reservation_to_read(item) for item in get_my_reservations(db, current_user)]


@router.get("/{reservation_id}/history", response_model=list[ReservationHistoryRead])
def get_current_user_reservation_history(
    reservation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ReservationHistoryRead]:
    events = get_history_for_customer(db, current_user, reservation_id)
    return [reservation_history_to_read(event) for event in events]


@router.get("/merchant", response_model=list[ReservationRead])
def get_current_merchant_reservations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ReservationRead]:
    merchant = require_merchant_for_user(db, current_user)
    return [reservation_to_read(item) for item in get_reservations_for_merchant(db, merchant)]


@router.get("/pickup/{pickup_code}", response_model=ReservationRead)
def get_pickup_reservation(
    pickup_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReservationRead:
    merchant = require_merchant_for_user(db, current_user)
    reservation = get_reservation_by_pickup_code_for_merchant(db, merchant, pickup_code)
    return reservation_to_read(reservation)


@router.post("/pickup/confirm", response_model=PickupConfirmResponse)
def confirm_pickup(
    payload: PickupConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PickupConfirmResponse:
    merchant = require_merchant_for_user(db, current_user)
    reservation = confirm_pickup_by_code(db, merchant, payload)
    return PickupConfirmResponse(reservation=reservation_to_read(reservation))


@router.patch("/{reservation_id}/cancel", response_model=ReservationRead)
def cancel_current_user_reservation(
    reservation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReservationRead:
    reservation = cancel_reservation(db, current_user, reservation_id)
    return reservation_to_read(reservation)


@router.post("/{reservation_id}/cancel", response_model=ReservationRead)
def cancel_current_user_reservation_post(
    reservation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReservationRead:
    reservation = cancel_reservation(db, current_user, reservation_id)
    return reservation_to_read(reservation)


@router.patch("/{reservation_id}/status", response_model=ReservationRead)
def update_current_merchant_reservation_status(
    reservation_id: UUID,
    payload: ReservationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReservationRead:
    merchant = require_merchant_for_user(db, current_user)
    reservation = update_reservation_status(db, merchant, reservation_id, payload)
    return reservation_to_read(reservation)


@router.patch("/{reservation_id}/delivery-status", response_model=ReservationRead)
def update_current_merchant_delivery_status(
    reservation_id: UUID,
    payload: DeliveryStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ReservationRead:
    merchant = require_merchant_for_user(db, current_user)
    reservation = update_delivery_status_for_merchant(db, merchant, reservation_id, payload)
    return reservation_to_read(reservation)


@store_router.get("/{store_id}/reservations", response_model=list[ReservationRead])
def get_current_merchant_store_reservations(
    store_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ReservationRead]:
    merchant = require_merchant_for_user(db, current_user)
    reservations = get_store_reservations_for_merchant(db, merchant, store_id)
    return [reservation_to_read(item) for item in reservations]


@merchant_router.get("/{reservation_id}/history", response_model=list[ReservationHistoryRead])
def get_current_merchant_reservation_history(
    reservation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ReservationHistoryRead]:
    merchant = require_merchant_for_user(db, current_user)
    events = get_history_for_merchant(db, merchant, reservation_id)
    return [reservation_history_to_read(event) for event in events]
