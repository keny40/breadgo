from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment import Payment, PaymentStatus
from app.models.product import Product, ProductStatus
from app.models.reservation import Reservation, ReservationStatus
from app.models.user import User
from app.schemas.payment import PaymentCancelRequest, PaymentConfirmRequest, PaymentFailRequest, PaymentReadyRequest
from app.services.reservation_history_service import record_reservation_history
from app.services.settlement_service import sync_settlement_for_payment


ACTIVE_PAYMENT_STATUSES = {PaymentStatus.READY, PaymentStatus.PAID}


def _get_user_reservation(db: Session, user: User, reservation_id: UUID) -> Reservation:
    reservation = db.scalar(
        select(Reservation).where(
            Reservation.id == reservation_id,
            Reservation.user_id == user.id,
        )
    )
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found.")
    return reservation


def _get_user_payment(db: Session, user: User, payment_id: UUID) -> Payment:
    payment = db.scalar(
        select(Payment).where(
            Payment.id == payment_id,
            Payment.user_id == user.id,
        )
    )
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")
    return payment


def create_mock_payment_ready(db: Session, user: User, payload: PaymentReadyRequest) -> Payment:
    reservation = _get_user_reservation(db, user, payload.reservation_id)
    duplicate = db.scalar(
        select(Payment).where(
            Payment.reservation_id == reservation.id,
            Payment.status.in_(ACTIVE_PAYMENT_STATUSES),
        )
    )
    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active payment already exists for this reservation.",
        )

    payment = Payment(
        reservation_id=reservation.id,
        user_id=user.id,
        amount=reservation.total_price,
        method=payload.method,
        status=PaymentStatus.READY,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def confirm_mock_payment(db: Session, user: User, payload: PaymentConfirmRequest) -> Payment:
    payment = _get_user_payment(db, user, payload.payment_id)
    if payment.status != PaymentStatus.READY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only READY payments can be confirmed.",
        )

    previous_status = payment.status
    payment.status = PaymentStatus.PAID
    payment.paid_at = datetime.now(timezone.utc)
    sync_settlement_for_payment(db, payment)
    record_reservation_history(
        db,
        reservation_id=payment.reservation_id,
        event_type="PAYMENT_COMPLETED",
        actor=user,
        from_status=previous_status,
        to_status=payment.status,
        message="결제 완료",
    )
    db.commit()
    db.refresh(payment)
    return payment


def fail_mock_payment(db: Session, user: User, payload: PaymentFailRequest) -> Payment:
    payment = _get_user_payment(db, user, payload.payment_id)
    if payment.status not in {PaymentStatus.READY, PaymentStatus.FAILED}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment cannot be failed in its current status.",
        )

    payment.status = PaymentStatus.FAILED
    sync_settlement_for_payment(db, payment)
    db.commit()
    db.refresh(payment)
    return payment


def cancel_mock_payment(db: Session, user: User, payload: PaymentCancelRequest) -> Payment:
    payment = _get_user_payment(db, user, payload.payment_id)
    reservation = db.scalar(
        select(Reservation)
        .where(Reservation.id == payment.reservation_id)
        .with_for_update()
    )
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found.")

    if reservation.status == ReservationStatus.PICKED_UP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment cannot be cancelled after pickup.",
        )

    if payment.status in {PaymentStatus.CANCELLED, PaymentStatus.REFUNDED}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment is already cancelled.",
        )

    previous_reservation_status = reservation.status
    previous_payment_status = payment.status

    if reservation.status != ReservationStatus.CANCELLED:
        product = db.scalar(
            select(Product)
            .where(Product.id == reservation.product_id)
            .with_for_update()
        )
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

        product.quantity += reservation.quantity
        if product.quantity > 0 and product.status == ProductStatus.SOLD_OUT:
            product.status = ProductStatus.ACTIVE
        reservation.status = ReservationStatus.CANCELLED
        record_reservation_history(
            db,
            reservation_id=reservation.id,
            event_type="RESERVATION_CANCELLED",
            actor=user,
            from_status=previous_reservation_status,
            to_status=reservation.status,
            message="예약 취소",
        )

    payment.status = PaymentStatus.CANCELLED
    payment.cancelled_at = datetime.now(timezone.utc)
    sync_settlement_for_payment(db, payment)
    record_reservation_history(
        db,
        reservation_id=reservation.id,
        event_type="MOCK_REFUND_PROCESSED",
        actor=user,
        from_status=previous_payment_status,
        to_status=payment.status,
        message="Mock 환불 처리",
    )
    db.commit()
    db.refresh(payment)
    return payment


def get_my_payments(db: Session, user: User) -> list[Payment]:
    return list(
        db.scalars(
            select(Payment)
            .where(Payment.user_id == user.id)
            .order_by(Payment.created_at.desc())
        )
    )


def get_all_payments_for_admin(db: Session) -> list[Payment]:
    return list(db.scalars(select(Payment).order_by(Payment.created_at.desc())))
