from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.payment import (
    PaymentCancelRequest,
    PaymentConfirmRequest,
    PaymentFailRequest,
    PaymentRead,
    PaymentReadyRequest,
)
from app.services.payment_service import (
    cancel_mock_payment,
    confirm_mock_payment,
    create_mock_payment_ready,
    fail_mock_payment,
    get_my_payments,
)


router = APIRouter()


@router.post("/mock/ready", response_model=PaymentRead, status_code=status.HTTP_201_CREATED)
def create_ready_payment(
    payload: PaymentReadyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentRead:
    payment = create_mock_payment_ready(db, current_user, payload)
    return PaymentRead.model_validate(payment)


@router.post("/mock/confirm", response_model=PaymentRead)
def confirm_payment(
    payload: PaymentConfirmRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentRead:
    payment = confirm_mock_payment(db, current_user, payload)
    return PaymentRead.model_validate(payment)


@router.post("/mock/fail", response_model=PaymentRead)
def fail_payment(
    payload: PaymentFailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentRead:
    payment = fail_mock_payment(db, current_user, payload)
    return PaymentRead.model_validate(payment)


@router.post("/mock/cancel", response_model=PaymentRead)
def cancel_payment(
    payload: PaymentCancelRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaymentRead:
    payment = cancel_mock_payment(db, current_user, payload)
    return PaymentRead.model_validate(payment)


@router.get("/me", response_model=list[PaymentRead])
def list_my_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PaymentRead]:
    return [PaymentRead.model_validate(payment) for payment in get_my_payments(db, current_user)]
