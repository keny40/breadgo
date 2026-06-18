from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.merchant import Merchant
from app.models.store import Store
from app.models.user import User, UserRole
from app.schemas.merchant import MerchantCreate
from app.schemas.settlement_account import SettlementAccountUpdate
from app.schemas.store import StoreCreate, StoreUpdate


def create_merchant_for_user(db: Session, user: User, payload: MerchantCreate) -> Merchant:
    existing_merchant = get_merchant_by_user(db, user)
    if existing_merchant is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a merchant profile.",
        )

    merchant = Merchant(
        user_id=user.id,
        business_name=payload.business_name.strip(),
        business_registration_number=payload.business_registration_number.strip(),
        representative_name=payload.representative_name.strip(),
        phone_number=payload.phone_number.strip(),
    )
    user.role = UserRole.MERCHANT
    db.add(merchant)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Merchant profile with this business registration number already exists.",
        ) from exc

    db.refresh(merchant)
    return merchant


def get_merchant_by_user(db: Session, user: User) -> Merchant | None:
    return db.scalar(select(Merchant).where(Merchant.user_id == user.id))


def require_merchant_for_user(db: Session, user: User) -> Merchant:
    merchant = get_merchant_by_user(db, user)
    if merchant is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Merchant profile is required for this action.",
        )
    return merchant


def get_merchant_by_id(db: Session, merchant_id: UUID) -> Merchant:
    merchant = db.scalar(select(Merchant).where(Merchant.id == merchant_id))
    if merchant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant not found.")
    return merchant


def update_settlement_account(
    db: Session,
    merchant: Merchant,
    payload: SettlementAccountUpdate,
) -> Merchant:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip() or None
        setattr(merchant, field, value)

    db.commit()
    db.refresh(merchant)
    return merchant


def create_store_for_merchant(db: Session, merchant: Merchant, payload: StoreCreate) -> Store:
    store = Store(
        merchant_id=merchant.id,
        name=payload.name.strip(),
        address=payload.address.strip(),
        address_detail=payload.address_detail.strip() if payload.address_detail else None,
        sido=payload.sido.strip() if payload.sido else None,
        sigungu=payload.sigungu.strip() if payload.sigungu else None,
        dong=payload.dong.strip() if payload.dong else None,
        latitude=payload.latitude,
        longitude=payload.longitude,
        phone_number=payload.phone_number.strip(),
        description=payload.description.strip() if payload.description else None,
        opening_time=payload.opening_time,
        closing_time=payload.closing_time,
    )
    db.add(store)
    db.commit()
    db.refresh(store)
    return store


def get_stores_by_merchant(db: Session, merchant: Merchant) -> list[Store]:
    return list(
        db.scalars(
            select(Store)
            .where(Store.merchant_id == merchant.id)
            .order_by(Store.created_at.desc())
        )
    )


def get_active_stores(db: Session) -> list[Store]:
    return list(
        db.scalars(
            select(Store)
            .where(Store.is_active.is_(True))
            .order_by(Store.created_at.desc())
        )
    )


def update_store(db: Session, merchant: Merchant, store_id: UUID, payload: StoreUpdate) -> Store:
    store = db.scalar(
        select(Store).where(
            Store.id == store_id,
            Store.merchant_id == merchant.id,
        )
    )
    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found.")

    update_data = payload.model_dump(exclude_unset=True)
    opening_time = update_data.get("opening_time", store.opening_time)
    closing_time = update_data.get("closing_time", store.closing_time)
    if opening_time >= closing_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="opening_time must be earlier than closing_time.",
        )

    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(store, field, value)

    db.commit()
    db.refresh(store)
    return store
