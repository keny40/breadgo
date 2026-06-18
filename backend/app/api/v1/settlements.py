from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.v1.admin import get_current_admin
from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.settlement import Settlement
from app.models.user import User
from app.schemas.settlement import SettlementRead, SettlementStatusUpdate, SettlementSummary
from app.services.merchant_service import require_merchant_for_user
from app.services.settlement_service import (
    build_settlement_summary,
    get_all_settlements,
    get_merchant_settlements,
    update_settlement_status,
)


admin_router = APIRouter()
merchant_router = APIRouter()


def settlement_to_read(settlement: Settlement) -> SettlementRead:
    payload = SettlementRead.model_validate(settlement)
    payload.store_name = settlement.store.name if settlement.store else None
    payload.merchant_name = settlement.merchant.business_name if settlement.merchant else None
    payload.merchant_email = settlement.merchant.user.email if settlement.merchant and settlement.merchant.user else None
    if settlement.merchant:
        payload.bank_name = settlement.merchant.bank_name
        payload.bank_account_number = settlement.merchant.bank_account_number
        payload.bank_account_holder = settlement.merchant.bank_account_holder
        payload.settlement_cycle = settlement.merchant.settlement_cycle
        payload.settlement_memo = settlement.merchant.settlement_memo
    if settlement.reservation:
        payload.reservation_status = settlement.reservation.status.value
        payload.pickup_code = settlement.reservation.pickup_code
        payload.fulfillment_method = settlement.reservation.fulfillment_method.value
        payload.delivery_fee = settlement.reservation.delivery_fee
        payload.delivery_status = settlement.reservation.delivery_status.value
        payload.product_name = settlement.reservation.product.name if settlement.reservation.product else None
    if settlement.payment:
        payload.payment_status = settlement.payment.status.value
    return payload


@admin_router.get("", response_model=list[SettlementRead])
def list_admin_settlements(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[SettlementRead]:
    return [settlement_to_read(item) for item in get_all_settlements(db)]


@admin_router.get("/summary", response_model=SettlementSummary)
def get_admin_settlement_summary(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> SettlementSummary:
    return build_settlement_summary(get_all_settlements(db))


@admin_router.patch("/{settlement_id}/status", response_model=SettlementRead)
def change_settlement_status(
    settlement_id: UUID,
    payload: SettlementStatusUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> SettlementRead:
    return settlement_to_read(update_settlement_status(db, settlement_id, payload, actor=current_admin))


@merchant_router.get("", response_model=list[SettlementRead])
def list_merchant_settlements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[SettlementRead]:
    merchant = require_merchant_for_user(db, current_user)
    return [settlement_to_read(item) for item in get_merchant_settlements(db, merchant)]


@merchant_router.get("/summary", response_model=SettlementSummary)
def get_merchant_settlement_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SettlementSummary:
    merchant = require_merchant_for_user(db, current_user)
    return build_settlement_summary(get_merchant_settlements(db, merchant))
