from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.models.payment import PaymentMethod, PaymentStatus


@dataclass(frozen=True)
class PaymentProviderResult:
    provider: str
    status: PaymentStatus
    amount: Decimal
    method: PaymentMethod
    external_payment_id: str | None = None
    message: str | None = None


class PaymentProviderAdapter:
    provider_name: str

    def ready(self, reservation_id: UUID, amount: Decimal, method: PaymentMethod) -> PaymentProviderResult:
        raise NotImplementedError

    def confirm(self, payment_id: UUID, amount: Decimal, method: PaymentMethod) -> PaymentProviderResult:
        raise NotImplementedError

    def fail(self, payment_id: UUID, amount: Decimal, method: PaymentMethod) -> PaymentProviderResult:
        raise NotImplementedError

    def cancel(self, payment_id: UUID, amount: Decimal, method: PaymentMethod) -> PaymentProviderResult:
        raise NotImplementedError
