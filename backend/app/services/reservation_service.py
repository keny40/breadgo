import secrets
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.merchant import Merchant
from app.models.payment import Payment, PaymentStatus
from app.models.product import Product, ProductStatus
from app.models.reservation import DeliveryStatus, FulfillmentMethod, Reservation, ReservationStatus
from app.models.store import Store
from app.models.user import User
from app.schemas.reservation import (
    DeliveryStatusUpdate,
    PickupConfirmRequest,
    ReservationCreate,
    ReservationStatusUpdate,
)
from app.services.notification_service import create_admin_notifications, create_notification
from app.services.reservation_history_service import record_reservation_history
from app.services.settlement_service import (
    mark_settlement_cancelled_for_reservation,
    mark_settlement_ready_for_reservation,
)


logger = get_logger("reservations")


def _generate_pickup_code(db: Session) -> str:
    for _ in range(20):
        code = f"{secrets.randbelow(1_000_000):06d}"
        existing = db.scalar(select(Reservation.id).where(Reservation.pickup_code == code))
        if existing is None:
            return code
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not generate pickup code.",
    )


def _get_reservation_for_user(db: Session, user: User, reservation_id: UUID) -> Reservation:
    reservation = db.scalar(
        select(Reservation).where(
            Reservation.id == reservation_id,
            Reservation.user_id == user.id,
        )
    )
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found.")
    return reservation


def _get_reservation_for_merchant(db: Session, merchant: Merchant, reservation_id: UUID) -> Reservation:
    reservation = db.scalar(
        select(Reservation)
        .join(Store, Reservation.store_id == Store.id)
        .where(
            Reservation.id == reservation_id,
            Store.merchant_id == merchant.id,
        )
    )
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found.")
    return reservation


def get_reservation_by_pickup_code_for_merchant(
    db: Session,
    merchant: Merchant,
    pickup_code: str,
) -> Reservation:
    reservation = db.scalar(
        select(Reservation)
        .join(Store, Reservation.store_id == Store.id)
        .where(
            Reservation.pickup_code == pickup_code,
            Store.merchant_id == merchant.id,
        )
    )
    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation with this pickup code was not found.",
        )
    return reservation


def _restore_product_quantity(product: Product, quantity: int) -> None:
    product.quantity += quantity
    if product.quantity > 0 and product.status == ProductStatus.SOLD_OUT:
        product.status = ProductStatus.ACTIVE


def create_reservation(db: Session, user: User, payload: ReservationCreate) -> Reservation:
    product = db.scalar(
        select(Product)
        .where(Product.id == payload.product_id)
        .with_for_update()
    )
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    if product.status != ProductStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product is not active.")

    if product.quantity < payload.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient product quantity.",
        )

    if payload.fulfillment_method == FulfillmentMethod.PICKUP:
        if not product.allow_pickup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pickup is not available for this product.",
            )
        delivery_fee = Decimal("0.00")
    elif payload.fulfillment_method == FulfillmentMethod.QUICK_DELIVERY:
        if not product.allow_quick_delivery:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quick delivery is not available for this product.",
            )
        delivery_fee = product.quick_delivery_fee
    else:
        if not product.allow_parcel_delivery:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parcel delivery is not available for this product.",
            )
        delivery_fee = product.parcel_delivery_fee

    product_amount = product.discount_price * payload.quantity
    delivery_status = (
        DeliveryStatus.NOT_REQUIRED
        if payload.fulfillment_method == FulfillmentMethod.PICKUP
        else DeliveryStatus.REQUESTED
    )

    if payload.fulfillment_method != FulfillmentMethod.PICKUP:
        missing_delivery_info = not (
            payload.recipient_name
            and payload.recipient_phone
            and payload.delivery_address
        )
        if missing_delivery_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recipient name, phone, and delivery address are required for delivery.",
            )

    product.quantity -= payload.quantity
    if product.quantity == 0:
        product.status = ProductStatus.SOLD_OUT

    reservation = Reservation(
        user_id=user.id,
        product_id=product.id,
        store_id=product.store_id,
        quantity=payload.quantity,
        product_amount=product_amount,
        delivery_fee=delivery_fee,
        total_price=product_amount + delivery_fee,
        fulfillment_method=payload.fulfillment_method,
        recipient_name=payload.recipient_name.strip() if payload.recipient_name else None,
        recipient_phone=payload.recipient_phone.strip() if payload.recipient_phone else None,
        delivery_address=payload.delivery_address.strip() if payload.delivery_address else None,
        delivery_request_memo=payload.delivery_request_memo.strip() if payload.delivery_request_memo else None,
        delivery_status=delivery_status,
        status=ReservationStatus.CONFIRMED,
        pickup_code=_generate_pickup_code(db),
        reserved_at=datetime.now(timezone.utc),
        pickup_deadline=product.pickup_end_time,
    )
    db.add(reservation)
    db.flush()
    record_reservation_history(
        db,
        reservation_id=reservation.id,
        event_type="RESERVATION_CREATED",
        actor=user,
        from_status=None,
        to_status=reservation.status,
        message="예약 생성",
    )
    db.commit()
    db.refresh(reservation)
    return reservation


def get_my_reservations(db: Session, user: User) -> list[Reservation]:
    return list(
        db.scalars(
            select(Reservation)
            .where(Reservation.user_id == user.id)
            .order_by(Reservation.created_at.desc())
        )
    )


def get_store_reservations_for_merchant(
    db: Session,
    merchant: Merchant,
    store_id: UUID,
) -> list[Reservation]:
    store = db.scalar(
        select(Store).where(
            Store.id == store_id,
            Store.merchant_id == merchant.id,
        )
    )
    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found.")

    return list(
        db.scalars(
            select(Reservation)
            .where(Reservation.store_id == store.id)
            .order_by(Reservation.created_at.desc())
        )
    )


def get_reservations_for_merchant(db: Session, merchant: Merchant) -> list[Reservation]:
    return list(
        db.scalars(
            select(Reservation)
            .join(Store, Reservation.store_id == Store.id)
            .where(Store.merchant_id == merchant.id)
            .order_by(Reservation.created_at.desc())
        )
    )


def cancel_reservation(db: Session, user: User, reservation_id: UUID) -> Reservation:
    reservation = _get_reservation_for_user(db, user, reservation_id)

    if reservation.status != ReservationStatus.CONFIRMED:
        logger.warning("Reservation cancel rejected. reservation_id=%s status=%s", reservation.id, reservation.status.value)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation cannot be cancelled.",
        )

    if reservation.delivery_status in {DeliveryStatus.SENT, DeliveryStatus.DELIVERED}:
        logger.warning(
            "Reservation cancel rejected by delivery status. reservation_id=%s delivery_status=%s",
            reservation.id,
            reservation.delivery_status.value,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery is already in progress or completed.",
        )

    payment = db.scalar(
        select(Payment)
        .where(
            Payment.reservation_id == reservation.id,
            Payment.user_id == user.id,
        )
        .with_for_update()
    )
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")

    if payment.status != PaymentStatus.PAID:
        logger.warning("Reservation cancel rejected by payment status. reservation_id=%s payment_status=%s", reservation.id, payment.status.value)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only paid reservations can be cancelled.",
        )

    product = db.scalar(
        select(Product)
        .where(Product.id == reservation.product_id)
        .with_for_update()
    )
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    previous_reservation_status = reservation.status
    previous_payment_status = payment.status
    _restore_product_quantity(product, reservation.quantity)
    reservation.status = ReservationStatus.CANCELLED
    if reservation.fulfillment_method != FulfillmentMethod.PICKUP:
        reservation.delivery_status = DeliveryStatus.CANCELLED
    payment.status = PaymentStatus.REFUNDED
    payment.cancelled_at = datetime.now(timezone.utc)
    mark_settlement_cancelled_for_reservation(db, reservation)
    create_notification(
        db,
        user=user,
        title="예약이 취소되었습니다.",
        message="예약이 취소되었고 상품 재고가 복구되었습니다.",
        notification_type="RESERVATION_CANCELLED",
        related_reservation_id=reservation.id,
        related_payment_id=payment.id,
    )
    create_notification(
        db,
        user=user,
        title="Mock 환불 처리되었습니다.",
        message="현재는 실제 PG 환불이 아닌 MVP용 Mock 환불 상태입니다.",
        notification_type="MOCK_REFUNDED",
        related_reservation_id=reservation.id,
        related_payment_id=payment.id,
    )
    if reservation.store and reservation.store.merchant:
        create_notification(
            db,
            user=reservation.store.merchant.user,
            role="MERCHANT",
            title="고객 예약이 취소되었습니다.",
            message="고객이 결제 완료 예약을 취소했습니다.",
            notification_type="RESERVATION_CANCELLED",
            related_reservation_id=reservation.id,
            related_payment_id=payment.id,
        )
    create_admin_notifications(
        db,
        title="예약 취소 및 Mock 환불이 발생했습니다.",
        message="고객 예약이 취소되고 Mock 환불 처리되었습니다.",
        notification_type="MOCK_REFUNDED",
        related_reservation_id=reservation.id,
        related_payment_id=payment.id,
    )
    record_reservation_history(
        db,
        reservation_id=reservation.id,
        event_type="RESERVATION_CANCELLED",
        actor=user,
        from_status=previous_reservation_status,
        to_status=reservation.status,
        message="예약 취소",
    )
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
    db.refresh(reservation)
    return reservation


def update_reservation_status(
    db: Session,
    merchant: Merchant,
    reservation_id: UUID,
    payload: ReservationStatusUpdate,
) -> Reservation:
    reservation = _get_reservation_for_merchant(db, merchant, reservation_id)

    if reservation.status == ReservationStatus.CANCELLED and payload.status != ReservationStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancelled reservations cannot be reopened.",
        )

    previous_status = reservation.status
    reservation.status = payload.status
    settlement = None
    if reservation.status == ReservationStatus.PICKED_UP:
        settlement = mark_settlement_ready_for_reservation(db, reservation)
    elif reservation.status == ReservationStatus.CANCELLED:
        mark_settlement_cancelled_for_reservation(db, reservation)
    record_reservation_history(
        db,
        reservation_id=reservation.id,
        event_type="PICKUP_CONFIRMED" if reservation.status == ReservationStatus.PICKED_UP else "RESERVATION_STATUS_CHANGED",
        actor=merchant.user,
        from_status=previous_status,
        to_status=reservation.status,
        message="픽업 완료" if reservation.status == ReservationStatus.PICKED_UP else "예약 상태 변경",
    )
    if reservation.status == ReservationStatus.PICKED_UP:
        create_notification(
            db,
            user=reservation.user,
            title="픽업이 완료되었습니다.",
            message="예약 상품 픽업이 완료 처리되었습니다.",
            notification_type="PICKUP_CONFIRMED",
            related_reservation_id=reservation.id,
            related_settlement_id=settlement.id if settlement else None,
        )
        create_notification(
            db,
            user=merchant.user,
            role="MERCHANT",
            title="픽업이 완료되었습니다.",
            message="고객 픽업을 완료 처리했습니다.",
            notification_type="PICKUP_CONFIRMED",
            related_reservation_id=reservation.id,
            related_settlement_id=settlement.id if settlement else None,
        )
        if settlement:
            create_notification(
                db,
                user=merchant.user,
                role="MERCHANT",
                title="정산 가능 상태가 되었습니다.",
                message="픽업 완료된 결제 건이 정산 가능 상태가 되었습니다.",
                notification_type="SETTLEMENT_READY",
                related_reservation_id=reservation.id,
                related_settlement_id=settlement.id,
            )
            create_admin_notifications(
                db,
                title="새 정산 가능 건이 생성되었습니다.",
                message="픽업 완료된 결제 건이 정산 가능 상태가 되었습니다.",
                notification_type="SETTLEMENT_READY",
                related_reservation_id=reservation.id,
                related_settlement_id=settlement.id,
            )
    db.commit()
    db.refresh(reservation)
    return reservation


def update_delivery_status_for_merchant(
    db: Session,
    merchant: Merchant,
    reservation_id: UUID,
    payload: DeliveryStatusUpdate,
) -> Reservation:
    reservation = _get_reservation_for_merchant(db, merchant, reservation_id)
    return _update_delivery_status(db, reservation, payload, actor=merchant.user)


def update_delivery_status_for_admin(
    db: Session,
    reservation_id: UUID,
    payload: DeliveryStatusUpdate,
    actor: User,
) -> Reservation:
    reservation = db.scalar(select(Reservation).where(Reservation.id == reservation_id))
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found.")
    return _update_delivery_status(db, reservation, payload, actor=actor)


def _update_delivery_status(
    db: Session,
    reservation: Reservation,
    payload: DeliveryStatusUpdate,
    actor: User | None = None,
) -> Reservation:
    if reservation.fulfillment_method == FulfillmentMethod.PICKUP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pickup reservations do not require delivery status.",
        )

    previous_status = reservation.delivery_status
    reservation.delivery_status = payload.delivery_status
    record_reservation_history(
        db,
        reservation_id=reservation.id,
        event_type="DELIVERY_STATUS_CHANGED",
        actor=actor,
        from_status=previous_status,
        to_status=reservation.delivery_status,
        message="배송 상태 변경",
    )
    create_notification(
        db,
        user=reservation.user,
        title="배송 상태가 변경되었습니다.",
        message=f"배송 상태가 {reservation.delivery_status.value}(으)로 변경되었습니다.",
        notification_type="DELIVERY_STATUS_CHANGED",
        related_reservation_id=reservation.id,
    )
    db.commit()
    db.refresh(reservation)
    return reservation


def confirm_pickup_by_code(
    db: Session,
    merchant: Merchant,
    payload: PickupConfirmRequest,
) -> Reservation:
    reservation = get_reservation_by_pickup_code_for_merchant(
        db=db,
        merchant=merchant,
        pickup_code=payload.pickup_code,
    )

    if reservation.status not in {ReservationStatus.PENDING, ReservationStatus.CONFIRMED}:
        logger.warning("Pickup confirm rejected. reservation_id=%s status=%s", reservation.id, reservation.status.value)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation cannot be picked up in its current status.",
        )

    previous_status = reservation.status
    reservation.status = ReservationStatus.PICKED_UP
    settlement = mark_settlement_ready_for_reservation(db, reservation)
    record_reservation_history(
        db,
        reservation_id=reservation.id,
        event_type="PICKUP_CONFIRMED",
        actor=merchant.user,
        from_status=previous_status,
        to_status=reservation.status,
        message="픽업 완료",
    )
    create_notification(
        db,
        user=reservation.user,
        title="픽업이 완료되었습니다.",
        message="예약 상품 픽업이 완료 처리되었습니다.",
        notification_type="PICKUP_CONFIRMED",
        related_reservation_id=reservation.id,
        related_settlement_id=settlement.id if settlement else None,
    )
    create_notification(
        db,
        user=merchant.user,
        role="MERCHANT",
        title="픽업이 완료되었습니다.",
        message="고객 픽업을 완료 처리했습니다.",
        notification_type="PICKUP_CONFIRMED",
        related_reservation_id=reservation.id,
        related_settlement_id=settlement.id if settlement else None,
    )
    if settlement:
        create_notification(
            db,
            user=merchant.user,
            role="MERCHANT",
            title="정산 가능 상태가 되었습니다.",
            message="픽업 완료된 결제 건이 정산 가능 상태가 되었습니다.",
            notification_type="SETTLEMENT_READY",
            related_reservation_id=reservation.id,
            related_settlement_id=settlement.id,
        )
        create_admin_notifications(
            db,
            title="새 정산 가능 건이 생성되었습니다.",
            message="픽업 완료된 결제 건이 정산 가능 상태가 되었습니다.",
            notification_type="SETTLEMENT_READY",
            related_reservation_id=reservation.id,
            related_settlement_id=settlement.id,
        )
    db.commit()
    db.refresh(reservation)
    return reservation
