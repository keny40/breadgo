from dataclasses import dataclass

from app.services.notification_provider.base import NotificationProviderPayload
from app.services.notification_provider.mock import MockNotificationProvider
from app.services.notification_provider.noop import NoopNotificationProvider


@dataclass(frozen=True)
class NotificationProviderDryRunResult:
    provider: str
    readiness_status: str
    delivered: bool
    skipped: bool
    external_calls_enabled: bool
    message: str


def get_notification_provider_readiness() -> list[object]:
    return [
        MockNotificationProvider().validate_connection(),
        NoopNotificationProvider().validate_connection(),
    ]


def run_mock_notification_provider_dry_run() -> NotificationProviderDryRunResult:
    provider = MockNotificationProvider()
    readiness = provider.validate_connection()
    result = provider.send_message(
        NotificationProviderPayload(
            title="Phase 129 dry-run",
            message="Adapter readiness dry-run only.",
            channel="IN_APP",
        )
    )
    external_calls_enabled = readiness.external_calls_enabled or result.external_calls_enabled

    return NotificationProviderDryRunResult(
        provider=provider.provider_name,
        readiness_status=readiness.status,
        delivered=result.delivered,
        skipped=result.skipped,
        external_calls_enabled=external_calls_enabled,
        message=(
            "Notification provider dry-run completed with MockNotificationProvider. "
            "No Email/Kakao/Push/Slack/Webhook calls were performed."
        ),
    )


def assert_mock_notification_provider_ready() -> None:
    result = run_mock_notification_provider_dry_run()
    if result.readiness_status != "READY" or not result.delivered:
        raise RuntimeError(f"NOTIFICATION_PROVIDER_MOCK_DRY_RUN_FAILED: {result}")
    if result.external_calls_enabled:
        raise RuntimeError("NOTIFICATION_PROVIDER_EXTERNAL_CALL_ENABLED")
