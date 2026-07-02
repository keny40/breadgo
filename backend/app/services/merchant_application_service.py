from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.merchant import Merchant, MerchantStatus
from app.models.merchant_application import MerchantApplication, MerchantApplicationStatus
from app.models.user import User, UserRole
from app.schemas.merchant_application import MerchantApplicationCreate, MerchantApplicationRejectRequest


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def create_merchant_application(db: Session, payload: MerchantApplicationCreate) -> MerchantApplication:
    email = payload.email.strip().lower()
    existing_pending = db.scalar(
        select(MerchantApplication).where(
            MerchantApplication.email == email,
            MerchantApplication.status == MerchantApplicationStatus.PENDING,
        )
    )
    if existing_pending is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending merchant application already exists for this email.",
        )
    existing_user = db.scalar(select(User).where(User.email == email))
    if existing_user is not None and existing_user.role in {UserRole.ADMIN, UserRole.MERCHANT}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email is already used by an admin or merchant account.",
        )

    application = MerchantApplication(
        store_name=payload.store_name.strip(),
        owner_name=payload.owner_name.strip(),
        email=email,
        password_hash=get_password_hash(payload.password),
        phone=payload.phone.strip(),
        business_registration_number=payload.business_registration_number.strip(),
        address=payload.address.strip(),
        region_sido=_clean_optional(payload.region_sido),
        region_sigungu=_clean_optional(payload.region_sigungu),
        region_dong=_clean_optional(payload.region_dong),
        product_category=_clean_optional(payload.product_category),
        pickup_available_time=_clean_optional(payload.pickup_available_time),
        note=_clean_optional(payload.note),
        status=MerchantApplicationStatus.PENDING,
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def list_merchant_applications(
    db: Session,
    status_filter: MerchantApplicationStatus | None = None,
) -> list[MerchantApplication]:
    statement = select(MerchantApplication).order_by(MerchantApplication.created_at.desc())
    if status_filter is not None:
        statement = statement.where(MerchantApplication.status == status_filter)
    return list(db.scalars(statement))


def get_merchant_application(db: Session, application_id: UUID) -> MerchantApplication:
    application = db.get(MerchantApplication, application_id)
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Merchant application not found.")
    return application


def approve_merchant_application(db: Session, application_id: UUID, actor: User) -> tuple[MerchantApplication, Merchant]:
    application = get_merchant_application(db, application_id)
    if application.status == MerchantApplicationStatus.APPROVED and application.merchant_id:
        merchant = db.get(Merchant, application.merchant_id)
        if merchant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approved merchant profile not found.")
        return application, merchant
    if application.status == MerchantApplicationStatus.REJECTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rejected applications cannot be approved.")

    user = db.scalar(select(User).where(User.email == application.email.lower()))
    if user is not None and user.role == UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin accounts cannot become merchants.")

    if user is None:
        if not application.password_hash:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Merchant application is missing a login password. Ask the merchant to submit a new application.",
            )
        user = User(
            email=application.email.lower(),
            phone=None,
            password_hash=application.password_hash,
            full_name=application.owner_name,
            role=UserRole.MERCHANT,
            is_active=True,
        )
        db.add(user)
        db.flush()
    else:
        if user.role == UserRole.CUSTOMER and application.password_hash:
            user.password_hash = application.password_hash
        user.role = UserRole.MERCHANT
        user.is_active = True

    existing_merchant = db.scalar(select(Merchant).where(Merchant.user_id == user.id))
    if existing_merchant is not None:
        merchant = existing_merchant
        merchant.status = MerchantStatus.APPROVED
    else:
        merchant = Merchant(
            user_id=user.id,
            business_name=application.store_name,
            business_registration_number=application.business_registration_number,
            representative_name=application.owner_name,
            phone_number=application.phone,
            status=MerchantStatus.APPROVED,
        )
        db.add(merchant)
        db.flush()

    now = datetime.now(timezone.utc)
    application.status = MerchantApplicationStatus.APPROVED
    application.rejection_reason = None
    application.reviewed_at = now
    application.reviewed_by_user_id = actor.id
    application.merchant_id = merchant.id

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Merchant profile could not be approved. Check duplicate email or business registration number.",
        ) from exc

    db.refresh(application)
    db.refresh(merchant)
    return application, merchant


def reject_merchant_application(
    db: Session,
    application_id: UUID,
    payload: MerchantApplicationRejectRequest,
    actor: User,
) -> MerchantApplication:
    application = get_merchant_application(db, application_id)
    if application.status == MerchantApplicationStatus.APPROVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Approved applications cannot be rejected.")

    application.status = MerchantApplicationStatus.REJECTED
    application.rejection_reason = payload.reason.strip()
    application.reviewed_at = datetime.now(timezone.utc)
    application.reviewed_by_user_id = actor.id
    db.commit()
    db.refresh(application)
    return application
