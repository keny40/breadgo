from dataclasses import dataclass

from app.services.delivery_provider.base import DeliveryQuoteRequest
from app.services.delivery_provider.mock import MockDeliveryProvider
from app.services.delivery_provider.noop import NoopDeliveryProvider


@dataclass(frozen=True)
class DeliveryProviderDryRunResult:
    provider: str
    readiness_status: str
    quote_fee: str
    create_status: str
    external_calls_enabled: bool
    message: str


def get_delivery_provider_readiness() -> list[object]:
    return [
        MockDeliveryProvider().validate_connection(),
        NoopDeliveryProvider().validate_connection(),
    ]


def run_mock_delivery_provider_dry_run() -> DeliveryProviderDryRunResult:
    provider = MockDeliveryProvider()
    request = DeliveryQuoteRequest(
        fulfillment_method="QUICK_DELIVERY",
        origin_region="서울특별시 강남구 역삼동",
        destination_region="서울특별시 강남구 역삼동",
        package_note="Phase 128 dry-run only",
    )
    readiness = provider.validate_connection()
    quote = provider.quote_delivery(request)
    created = provider.create_delivery(request)
    external_calls_enabled = (
        readiness.external_calls_enabled
        or quote.external_calls_enabled
        or created.external_calls_enabled
    )

    return DeliveryProviderDryRunResult(
        provider=provider.provider_name,
        readiness_status=readiness.status,
        quote_fee=str(quote.delivery_fee),
        create_status=created.delivery_status,
        external_calls_enabled=external_calls_enabled,
        message=(
            "Delivery provider dry-run completed with MockDeliveryProvider. "
            "No external delivery API calls were performed."
        ),
    )


def assert_mock_delivery_provider_ready() -> None:
    result = run_mock_delivery_provider_dry_run()
    if result.readiness_status != "READY" or result.create_status != "REQUESTED":
        raise RuntimeError(f"DELIVERY_PROVIDER_MOCK_DRY_RUN_FAILED: {result}")
    if result.external_calls_enabled:
        raise RuntimeError("DELIVERY_PROVIDER_EXTERNAL_CALL_ENABLED")
