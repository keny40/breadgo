from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException, status

from app.models.payment import PaymentMethod
from app.services.payments.base import PaymentProviderAdapter, PaymentProviderResult


class TossPaymentProvider(PaymentProviderAdapter):
    provider_name = "TOSS"

    def ready(self, reservation_id: UUID, amount: Decimal, method: PaymentMethod) -> PaymentProviderResult:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Toss Payments provider is designed but not enabled in this MVP phase.",
        )

    def confirm(self, payment_id: UUID, amount: Decimal, method: PaymentMethod) -> PaymentProviderResult:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Toss Payments confirmation is not enabled in this MVP phase.",
        )

    def fail(self, payment_id: UUID, amount: Decimal, method: PaymentMethod) -> PaymentProviderResult:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Toss Payments failure handling is not enabled in this MVP phase.",
        )

    def cancel(self, payment_id: UUID, amount: Decimal, method: PaymentMethod) -> PaymentProviderResult:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Toss Payments cancellation is not enabled in this MVP phase.",
        )
