from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.schemas.pos_integration import MockPosItem
from app.services.pos_providers.generic import GenericPosProvider
from app.services.pos_providers.mock import MockPosProvider


@dataclass(frozen=True)
class PosProviderReadiness:
    provider: str
    status: str
    mode: str
    external_calls_enabled: bool
    message: str


@dataclass(frozen=True)
class PosProviderDryRunResult:
    provider: str
    readiness_status: str
    normalized_item_count: int
    external_calls_enabled: bool
    message: str


def get_pos_provider_readiness() -> list[PosProviderReadiness]:
    generic_provider = GenericPosProvider()
    generic_ready, generic_message = generic_provider.validate_connection()
    return [
        PosProviderReadiness(
            provider="MOCK_POS",
            status="READY",
            mode="MOCK_ONLY",
            external_calls_enabled=False,
            message="Mock POS provider is available. No external POS API calls are performed.",
        ),
        PosProviderReadiness(
            provider=generic_provider.provider_name,
            status="READY" if generic_ready else "NOT_CONFIGURED",
            mode="NOOP_ONLY",
            external_calls_enabled=False,
            message=generic_message or "Generic POS provider is not configured in this demo phase.",
        ),
    ]


def run_mock_pos_provider_dry_run() -> PosProviderDryRunResult:
    now = datetime.now(timezone.utc)
    item = MockPosItem(
        external_sku="phase129-dry-run",
        name="Phase 129 Mock POS Item",
        description="Adapter readiness dry-run only.",
        original_price=Decimal("5000.00"),
        discount_price=Decimal("3500.00"),
        stock_quantity=3,
        sale_starts_at=now,
        sale_ends_at=now + timedelta(hours=2),
        pickup_available=True,
        quick_delivery_available=False,
        parcel_delivery_available=False,
        quick_delivery_fee=Decimal("0.00"),
        parcel_delivery_fee=Decimal("0.00"),
    )
    provider = MockPosProvider([item])
    ready, message = provider.validate_connection()
    normalized = [provider.normalize_item(raw_item) for raw_item in provider.fetch_items()]

    return PosProviderDryRunResult(
        provider=provider.provider_name,
        readiness_status="READY" if ready else "NOT_READY",
        normalized_item_count=len(normalized),
        external_calls_enabled=False,
        message=message or "POS provider dry-run completed with MockPosProvider. No external POS API calls were performed.",
    )


def assert_mock_pos_provider_ready() -> None:
    result = run_mock_pos_provider_dry_run()
    if result.readiness_status != "READY" or result.normalized_item_count < 1:
        raise RuntimeError(f"POS_PROVIDER_MOCK_DRY_RUN_FAILED: {result}")
    if result.external_calls_enabled:
        raise RuntimeError("POS_PROVIDER_EXTERNAL_CALL_ENABLED")
