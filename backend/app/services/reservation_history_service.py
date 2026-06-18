from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.merchant import Merchant
from app.models.reservation import Reservation
from app.models.reservation_history import ReservationHistory
from app.models.store import Store
from app.models.user import User


EVENT_MESSAGES = {
    "RESERVATION_CREATED": "예약 생성",
    "PAYMENT_COMPLETED": "결제 완료",
    "PICKUP_CONFIRMED": "픽업 완료",
    "DELIVERY_STATUS_CHANGED": "배송 상태 변경",
    "RESERVATION_CANCELLED": "예약 취소",
    "MOCK_REFUND_PROCESSED": "Mock 환불 처리",
    "SETTLEMENT_STATUS_CHANGED": "정산 상태 변경",
}


def _value(status_value: object | None) -> str | None:
    if status_value is None:
        return None
    value = getattr(status_value, "value", status_value)
    return str(value).upper()


def _role(user: User | None, fallback: str | None = None) -> str | None:
    if user is None:
        return fallback
    return _value(user.role)


def record_reservation_history(
    db: Session,
    reservation_id: UUID,
    event_type: str,
    actor: User | None = None,
    actor_role: str | None = None,
    from_status: object | None = None,
    to_status: object | None = None,
    message: str | None = None,
) -> ReservationHistory:
    event = ReservationHistory(
        reservation_id=reservation_id,
        actor_user_id=actor.id if actor else None,
        actor_role=_role(actor, actor_role),
        event_type=event_type,
        from_status=_value(from_status),
        to_status=_value(to_status),
        message=message or EVENT_MESSAGES.get(event_type, event_type),
    )
    db.add(event)
    return event


def get_history_for_customer(db: Session, user: User, reservation_id: UUID) -> list[ReservationHistory]:
    reservation = db.scalar(
        select(Reservation.id).where(
            Reservation.id == reservation_id,
            Reservation.user_id == user.id,
        )
    )
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found.")
    return _get_history(db, reservation_id)


def get_history_for_merchant(db: Session, merchant: Merchant, reservation_id: UUID) -> list[ReservationHistory]:
    reservation = db.scalar(
        select(Reservation.id)
        .join(Store, Reservation.store_id == Store.id)
        .where(
            Reservation.id == reservation_id,
            Store.merchant_id == merchant.id,
        )
    )
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found.")
    return _get_history(db, reservation_id)


def get_history_for_admin(db: Session, reservation_id: UUID) -> list[ReservationHistory]:
    reservation = db.scalar(select(Reservation.id).where(Reservation.id == reservation_id))
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found.")
    return _get_history(db, reservation_id)


def _get_history(db: Session, reservation_id: UUID) -> list[ReservationHistory]:
    return list(
        db.scalars(
            select(ReservationHistory)
            .where(ReservationHistory.reservation_id == reservation_id)
            .order_by(ReservationHistory.created_at.asc())
        )
    )
