from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.merchant import Merchant
from app.models.payment import Payment, PaymentStatus
from app.models.reservation import Reservation, ReservationStatus
from app.models.settlement import Settlement, SettlementStatus
from app.schemas.settlement import SettlementStatusUpdate, SettlementSummary


PLATFORM_FEE_RATE = Decimal("0.1000")
PG_FEE_RATE = Decimal("0.0300")
MONEY_QUANT = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def _calculate_amounts(gross_amount: Decimal) -> dict[str, Decimal]:
    platform_fee_amount = _money(gross_amount * PLATFORM_FEE_RATE)
    pg_fee_amount = _money(gross_amount * PG_FEE_RATE)
    merchant_settlement_amount = _money(gross_amount - platform_fee_amount - pg_fee_amount)
    return {
        "gross_amount": _money(gross_amount),
        "platform_fee_rate": PLATFORM_FEE_RATE,
        "platform_fee_amount": platform_fee_amount,
        "pg_fee_rate": PG_FEE_RATE,
        "pg_fee_amount": pg_fee_amount,
        "merchant_settlement_amount": merchant_settlement_amount,
    }


def _status_for_payment(payment: Payment) -> SettlementStatus:
    if payment.status in {PaymentStatus.CANCELLED, PaymentStatus.FAILED, PaymentStatus.REFUNDED}:
        return SettlementStatus.CANCELLED
    if payment.status != PaymentStatus.PAID:
        return SettlementStatus.PENDING
    if payment.reservation and payment.reservation.status == ReservationStatus.PICKED_UP:
        return SettlementStatus.READY
    return SettlementStatus.PENDING


def sync_settlement_for_payment(db: Session, payment: Payment) -> Settlement | None:
    if payment.reservation is None:
        reservation = db.scalar(select(Reservation).where(Reservation.id == payment.reservation_id))
        if reservation is None:
            return None
        payment.reservation = reservation

    if payment.status not in {PaymentStatus.PAID, PaymentStatus.CANCELLED, PaymentStatus.FAILED, PaymentStatus.REFUNDED}:
        return None

    settlement = db.scalar(select(Settlement).where(Settlement.payment_id == payment.id))
    if settlement is None:
        settlement = Settlement(
            merchant_id=payment.reservation.store.merchant_id,
            store_id=payment.reservation.store_id,
            reservation_id=payment.reservation.id,
            payment_id=payment.id,
            status=_status_for_payment(payment),
            **_calculate_amounts(payment.amount),
        )
        db.add(settlement)
        return settlement

    if settlement.status not in {SettlementStatus.PAID, SettlementStatus.HOLD}:
        settlement.status = _status_for_payment(payment)

    for field, value in _calculate_amounts(payment.amount).items():
        setattr(settlement, field, value)
    return settlement


def ensure_missing_settlements(db: Session) -> None:
    payments = list(
        db.scalars(
            select(Payment)
            .where(Payment.status.in_({PaymentStatus.PAID, PaymentStatus.CANCELLED, PaymentStatus.FAILED, PaymentStatus.REFUNDED}))
            .order_by(Payment.created_at.asc())
        )
    )
    changed = False
    for payment in payments:
        existing = db.scalar(select(Settlement.id).where(Settlement.payment_id == payment.id))
        if existing is None:
            settlement = sync_settlement_for_payment(db, payment)
            changed = changed or settlement is not None
    if changed:
        db.commit()


def mark_settlement_ready_for_reservation(db: Session, reservation: Reservation) -> Settlement | None:
    payment = reservation.payment
    if payment is None:
        payment = db.scalar(select(Payment).where(Payment.reservation_id == reservation.id))
    if payment is None or payment.status != PaymentStatus.PAID:
        return None

    settlement = sync_settlement_for_payment(db, payment)
    if settlement and settlement.status == SettlementStatus.PENDING:
        settlement.status = SettlementStatus.READY
    return settlement


def mark_settlement_cancelled_for_reservation(db: Session, reservation: Reservation) -> None:
    settlement = db.scalar(select(Settlement).where(Settlement.reservation_id == reservation.id))
    if settlement and settlement.status != SettlementStatus.PAID:
        settlement.status = SettlementStatus.CANCELLED


def get_all_settlements(db: Session) -> list[Settlement]:
    ensure_missing_settlements(db)
    return list(db.scalars(select(Settlement).order_by(Settlement.created_at.desc())))


def get_merchant_settlements(db: Session, merchant: Merchant) -> list[Settlement]:
    ensure_missing_settlements(db)
    return list(
        db.scalars(
            select(Settlement)
            .where(Settlement.merchant_id == merchant.id)
            .order_by(Settlement.created_at.desc())
        )
    )


def update_settlement_status(
    db: Session,
    settlement_id: UUID,
    payload: SettlementStatusUpdate,
) -> Settlement:
    settlement = db.scalar(select(Settlement).where(Settlement.id == settlement_id))
    if settlement is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settlement not found.")

    if payload.status not in {SettlementStatus.PAID, SettlementStatus.HOLD}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin can only mark settlements as PAID or HOLD.",
        )

    if payload.status == SettlementStatus.PAID and settlement.status == SettlementStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancelled settlements cannot be paid.",
        )

    settlement.status = payload.status
    settlement.settled_at = datetime.now(timezone.utc) if payload.status == SettlementStatus.PAID else None
    db.commit()
    db.refresh(settlement)
    return settlement


def build_settlement_summary(settlements: list[Settlement]) -> SettlementSummary:
    count_by_status = {status.value: 0 for status in SettlementStatus}
    amount_by_status = {status.value: Decimal("0.00") for status in SettlementStatus}
    total_gross_amount = Decimal("0.00")
    total_platform_fee_amount = Decimal("0.00")
    total_pg_fee_amount = Decimal("0.00")
    total_merchant_settlement_amount = Decimal("0.00")

    for settlement in settlements:
        status_value = settlement.status.value
        count_by_status[status_value] += 1
        amount_by_status[status_value] += settlement.merchant_settlement_amount
        if settlement.status != SettlementStatus.CANCELLED:
            total_gross_amount += settlement.gross_amount
            total_platform_fee_amount += settlement.platform_fee_amount
            total_pg_fee_amount += settlement.pg_fee_amount
            total_merchant_settlement_amount += settlement.merchant_settlement_amount

    return SettlementSummary(
        total_gross_amount=_money(total_gross_amount),
        total_platform_fee_amount=_money(total_platform_fee_amount),
        total_pg_fee_amount=_money(total_pg_fee_amount),
        total_merchant_settlement_amount=_money(total_merchant_settlement_amount),
        pending_amount=_money(amount_by_status[SettlementStatus.PENDING.value]),
        ready_amount=_money(amount_by_status[SettlementStatus.READY.value]),
        paid_amount=_money(amount_by_status[SettlementStatus.PAID.value]),
        hold_amount=_money(amount_by_status[SettlementStatus.HOLD.value]),
        cancelled_amount=_money(amount_by_status[SettlementStatus.CANCELLED.value]),
        count_by_status=count_by_status,
    )
