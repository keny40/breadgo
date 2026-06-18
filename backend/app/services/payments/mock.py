from decimal import Decimal
from uuid import UUID

from app.models.payment import PaymentMethod, PaymentProvider, PaymentStatus
from app.services.payments.base import PaymentProviderAdapter, PaymentProviderResult


class MockPaymentProvider(PaymentProviderAdapter):
    provider_name = PaymentProvider.MOCK.value

    def ready(self, reservation_id: UUID, amount: Decimal, method: PaymentMethod) -> PaymentProviderResult:
        return PaymentProviderResult(
            provider=self.provider_name,
            status=PaymentStatus.READY,
            amount=amount,
            method=method,
            external_payment_id=f"mock-ready-{reservation_id}",
            message="Mock payment is ready.",
        )

    def confirm(self, payment_id: UUID, amount: Decimal, method: PaymentMethod) -> PaymentProviderResult:
        return PaymentProviderResult(
            provider=self.provider_name,
            status=PaymentStatus.PAID,
            amount=amount,
            method=method,
            external_payment_id=f"mock-paid-{payment_id}",
            message="Mock payment is paid.",
        )

    def fail(self, payment_id: UUID, amount: Decimal, method: PaymentMethod) -> PaymentProviderResult:
        return PaymentProviderResult(
            provider=self.provider_name,
            status=PaymentStatus.FAILED,
            amount=amount,
            method=method,
            external_payment_id=f"mock-failed-{payment_id}",
            message="Mock payment failed.",
        )

    def cancel(self, payment_id: UUID, amount: Decimal, method: PaymentMethod) -> PaymentProviderResult:
        return PaymentProviderResult(
            provider=self.provider_name,
            status=PaymentStatus.CANCELLED,
            amount=amount,
            method=method,
            external_payment_id=f"mock-cancelled-{payment_id}",
            message="Mock payment is cancelled.",
        )
