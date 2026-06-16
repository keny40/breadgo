from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.merchant import Merchant
from app.models.payment import Payment, PaymentStatus
from app.models.product import Product, ProductStatus
from app.models.reservation import Reservation, ReservationStatus
from app.models.store import Store
from app.models.user import User, UserRole
from app.schemas.admin import AdminSummary, MerchantStatusUpdate


def require_admin_user(user: User) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission is required.",
        )
    return user


def _count(db: Session, statement) -> int:
    return int(db.scalar(statement) or 0)


def get_admin_summary(db: Session) -> AdminSummary:
    return AdminSummary(
        total_users=_count(db, select(func.count()).select_from(User)),
        total_merchants=_count(db, select(func.count()).select_from(Merchant)),
        total_stores=_count(db, select(func.count()).select_from(Store)),
        total_products=_count(db, select(func.count()).select_from(Product)),
        active_products=_count(
            db,
            select(func.count()).select_from(Product).where(Product.status == ProductStatus.ACTIVE),
        ),
        total_reservations=_count(db, select(func.count()).select_from(Reservation)),
        picked_up_reservations=_count(
            db,
            select(func.count())
            .select_from(Reservation)
            .where(Reservation.status == ReservationStatus.PICKED_UP),
        ),
        cancelled_reservations=_count(
            db,
            select(func.count())
            .select_from(Reservation)
            .where(Reservation.status == ReservationStatus.CANCELLED),
        ),
        total_payments=_count(db, select(func.count()).select_from(Payment)),
        paid_payments=_count(
            db,
            select(func.count()).select_from(Payment).where(Payment.status == PaymentStatus.PAID),
        ),
        cancelled_payments=_count(
            db,
            select(func.count())
            .select_from(Payment)
            .where(Payment.status == PaymentStatus.CANCELLED),
        ),
        failed_payments=_count(
            db,
            select(func.count())
            .select_from(Payment)
            .where(Payment.status == PaymentStatus.FAILED),
        ),
        refunded_payments=_count(
            db,
            select(func.count())
            .select_from(Payment)
            .where(Payment.status == PaymentStatus.REFUNDED),
        ),
        total_paid_amount=db.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0))
            .select_from(Payment)
            .where(Payment.status == PaymentStatus.PAID)
        ),
    )


def get_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())))


def get_merchants(db: Session) -> list[Merchant]:
    return list(db.scalars(select(Merchant).order_by(Merchant.created_at.desc())))


def get_stores(db: Session) -> list[Store]:
    return list(db.scalars(select(Store).order_by(Store.created_at.desc())))


def get_products(db: Session) -> list[Product]:
    return list(db.scalars(select(Product).order_by(Product.created_at.desc())))


def get_reservations(db: Session) -> list[Reservation]:
    return list(db.scalars(select(Reservation).order_by(Reservation.created_at.desc())))


def get_payments(db: Session) -> list[Payment]:
    return list(db.scalars(select(Payment).order_by(Payment.created_at.desc())))


def update_merchant_status(db: Session, merchant_id: UUID, payload: MerchantStatusUpdate) -> Merchant:
    merchant = db.get(Merchant, merchant_id)
    if merchant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found.")

    merchant.status = payload.status
    db.commit()
    db.refresh(merchant)
    return merchant
