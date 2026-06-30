from dataclasses import asdict, dataclass

from app.services.delivery_provider_service import (
    get_delivery_provider_readiness,
    run_mock_delivery_provider_dry_run,
)
from app.services.notification_provider_service import (
    get_notification_provider_readiness,
    run_mock_notification_provider_dry_run,
)
from app.services.payment_provider_service import (
    get_payment_provider_readiness,
    run_mock_payment_provider_dry_run,
)
from app.services.pos_provider_service import get_pos_provider_readiness, run_mock_pos_provider_dry_run


@dataclass(frozen=True)
class ExternalIntegrationReadinessItem:
    area: str
    provider: str
    status: str
    mode: str
    external_calls_enabled: bool
    message: str


@dataclass(frozen=True)
class ExternalIntegrationDryRunItem:
    area: str
    provider: str
    status: str
    external_calls_enabled: bool
    message: str


@dataclass(frozen=True)
class ExternalIntegrationReadinessSummary:
    overall_status: str
    external_calls_enabled: bool
    message: str
    items: list[ExternalIntegrationReadinessItem]
    dry_runs: list[ExternalIntegrationDryRunItem]


def _readiness_item(area: str, readiness: object) -> ExternalIntegrationReadinessItem:
    data = asdict(readiness)
    return ExternalIntegrationReadinessItem(
        area=area,
        provider=str(data["provider"]),
        status=str(data["status"]),
        mode=str(data["mode"]),
        external_calls_enabled=bool(data["external_calls_enabled"]),
        message=str(data["message"]),
    )


def build_external_integration_readiness() -> ExternalIntegrationReadinessSummary:
    items = [
        *[_readiness_item("PAYMENT", item) for item in get_payment_provider_readiness()],
        *[_readiness_item("DELIVERY", item) for item in get_delivery_provider_readiness()],
        *[_readiness_item("NOTIFICATION", item) for item in get_notification_provider_readiness()],
        *[_readiness_item("POS", item) for item in get_pos_provider_readiness()],
    ]

    payment_dry_run = run_mock_payment_provider_dry_run()
    delivery_dry_run = run_mock_delivery_provider_dry_run()
    notification_dry_run = run_mock_notification_provider_dry_run()
    pos_dry_run = run_mock_pos_provider_dry_run()
    dry_runs = [
        ExternalIntegrationDryRunItem(
            area="PAYMENT",
            provider=payment_dry_run.provider,
            status=f"{payment_dry_run.ready_status}/{payment_dry_run.confirm_status}",
            external_calls_enabled=payment_dry_run.external_calls_enabled,
            message=payment_dry_run.message,
        ),
        ExternalIntegrationDryRunItem(
            area="DELIVERY",
            provider=delivery_dry_run.provider,
            status=f"{delivery_dry_run.readiness_status}/{delivery_dry_run.create_status}",
            external_calls_enabled=delivery_dry_run.external_calls_enabled,
            message=delivery_dry_run.message,
        ),
        ExternalIntegrationDryRunItem(
            area="NOTIFICATION",
            provider=notification_dry_run.provider,
            status=f"{notification_dry_run.readiness_status}/DELIVERED_{notification_dry_run.delivered}",
            external_calls_enabled=notification_dry_run.external_calls_enabled,
            message=notification_dry_run.message,
        ),
        ExternalIntegrationDryRunItem(
            area="POS",
            provider=pos_dry_run.provider,
            status=f"{pos_dry_run.readiness_status}/ITEMS_{pos_dry_run.normalized_item_count}",
            external_calls_enabled=pos_dry_run.external_calls_enabled,
            message=pos_dry_run.message,
        ),
    ]

    external_calls_enabled = any(item.external_calls_enabled for item in items) or any(
        item.external_calls_enabled for item in dry_runs
    )
    return ExternalIntegrationReadinessSummary(
        overall_status="CHECK_FAILED" if external_calls_enabled else "MOCK_READY",
        external_calls_enabled=external_calls_enabled,
        message=(
            "External integration adapters are ready for mock/noop dry-runs. "
            "No PG, delivery, POS, Email/Kakao/Push/Slack/Webhook calls are enabled."
        ),
        items=items,
        dry_runs=dry_runs,
    )


def assert_external_integration_readiness_ready() -> None:
    summary = build_external_integration_readiness()
    if summary.external_calls_enabled:
        raise RuntimeError(f"EXTERNAL_INTEGRATION_CALLS_ENABLED: {summary}")
    if summary.overall_status != "MOCK_READY":
        raise RuntimeError(f"EXTERNAL_INTEGRATION_READINESS_FAILED: {summary}")
