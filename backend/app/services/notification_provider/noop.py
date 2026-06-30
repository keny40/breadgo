from app.services.notification_provider.base import (
    NotificationProviderPayload,
    NotificationProviderReadiness,
    NotificationProviderSendResult,
)


class NoopNotificationProvider:
    provider_name = "NOOP_EXTERNAL_NOTIFICATION"

    def validate_connection(self) -> NotificationProviderReadiness:
        return NotificationProviderReadiness(
            provider=self.provider_name,
            status="NOT_ENABLED",
            mode="NOOP_ONLY",
            external_calls_enabled=False,
            message="External notification providers are intentionally disabled in this demo phase.",
        )

    def send_message(self, payload: NotificationProviderPayload) -> NotificationProviderSendResult:
        return NotificationProviderSendResult(
            provider=self.provider_name,
            channel=payload.channel,
            delivered=False,
            skipped=True,
            external_calls_enabled=False,
            message="External notification dry-run skipped. No Email/Kakao/Push/Slack/Webhook calls were performed.",
        )
