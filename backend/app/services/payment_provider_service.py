from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4

from app.models.payment import PaymentMethod, PaymentStatus
from app.services.payments.mock import MockPaymentProvider


@dataclass(frozen=True)
class PaymentProviderReadiness:
    provider: str
    status: str
    mode: str
    external_calls_enabled: bool
    message: str


@dataclass(frozen=True)
class PaymentProviderDryRunResult:
    provider: str
    ready_status: str
    confirm_status: str
    external_calls_enabled: bool
    message: str


def get_payment_provider_readiness() -> list[PaymentProviderReadiness]:
    return [
        PaymentProviderReadiness(
            provider="MOCK",
            status="READY",
            mode="MOCK_ONLY",
            external_calls_enabled=False,
            message="Mock payment provider is available. No external PG API calls are performed.",
        ),
        PaymentProviderReadiness(
            provider="TOSS",
            status="NOT_ENABLED",
            mode="SKELETON_ONLY",
            external_calls_enabled=False,
            message="Toss payment provider skeleton exists but is not enabled in this demo phase.",
        ),
    ]


def run_mock_payment_provider_dry_run() -> PaymentProviderDryRunResult:
    provider = MockPaymentProvider()
    reservation_id = uuid4()
    payment_id = uuid4()
    amount = Decimal("1000.00")
    method = PaymentMethod.MOCK_CARD

    ready_result = provider.ready(reservation_id=reservation_id, amount=amount, method=method)
    confirm_result = provider.confirm(payment_id=payment_id, amount=amount, method=method)

    return PaymentProviderDryRunResult(
        provider=provider.provider_name,
        ready_status=ready_result.status.value,
        confirm_status=confirm_result.status.value,
        external_calls_enabled=False,
        message=(
            "Payment provider dry-run completed with MockPaymentProvider. "
            "No external PG API calls were performed."
        ),
    )


def assert_mock_payment_provider_ready() -> None:
    result = run_mock_payment_provider_dry_run()
    if result.ready_status != PaymentStatus.READY.value or result.confirm_status != PaymentStatus.PAID.value:
        raise RuntimeError(f"PAYMENT_PROVIDER_MOCK_DRY_RUN_FAILED: {result}")
    if result.external_calls_enabled:
        raise RuntimeError("PAYMENT_PROVIDER_EXTERNAL_CALL_ENABLED")
