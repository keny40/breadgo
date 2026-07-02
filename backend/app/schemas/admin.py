from pydantic import BaseModel
from decimal import Decimal

from app.models.merchant import MerchantPlan, MerchantStatus
from app.models.user import UserStatus


class AdminSummary(BaseModel):
    total_users: int
    total_merchants: int
    total_stores: int
    total_products: int
    active_products: int
    total_reservations: int
    picked_up_reservations: int
    cancelled_reservations: int
    total_payments: int
    paid_payments: int
    cancelled_payments: int
    failed_payments: int
    refunded_payments: int
    total_paid_amount: Decimal


class MerchantStatusUpdate(BaseModel):
    status: MerchantStatus
    reason: str | None = None


class MerchantPlanUpdate(BaseModel):
    plan: MerchantPlan


class UserStatusUpdate(BaseModel):
    status: UserStatus
    reason: str | None = None


class DemoSeedResponse(BaseModel):
    users: int
    merchant: int
    stores: int
    products: int
    admin_user_id: str
    merchant_user_id: str
    customer_user_id: str
