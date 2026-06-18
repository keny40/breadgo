from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.admin import get_current_admin
from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.merchant import Merchant
from app.models.user import User
from app.schemas.settlement_account import SettlementAccountRead, SettlementAccountUpdate
from app.services.merchant_service import (
    get_merchant_by_id,
    require_merchant_for_user,
    update_settlement_account,
)


router = APIRouter()
admin_router = APIRouter()


def account_to_read(merchant: Merchant) -> SettlementAccountRead:
    return SettlementAccountRead(
        merchant_id=merchant.id,
        business_name=merchant.business_name,
        bank_name=merchant.bank_name,
        bank_account_number=merchant.bank_account_number,
        bank_account_holder=merchant.bank_account_holder,
        settlement_cycle=merchant.settlement_cycle,
        settlement_memo=merchant.settlement_memo,
        created_at=merchant.created_at,
        updated_at=merchant.updated_at,
    )


@router.get("", response_model=SettlementAccountRead)
def get_my_settlement_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SettlementAccountRead:
    merchant = require_merchant_for_user(db, current_user)
    return account_to_read(merchant)


@router.put("", response_model=SettlementAccountRead)
def update_my_settlement_account(
    payload: SettlementAccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SettlementAccountRead:
    merchant = require_merchant_for_user(db, current_user)
    return account_to_read(update_settlement_account(db, merchant, payload))


@admin_router.get("/{merchant_id}/settlement-account", response_model=SettlementAccountRead)
def get_merchant_settlement_account_for_admin(
    merchant_id: UUID,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> SettlementAccountRead:
    return account_to_read(get_merchant_by_id(db, merchant_id))
