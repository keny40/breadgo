from app.services.notification_provider.base import (
    NotificationProviderPayload,
    NotificationProviderReadiness,
    NotificationProviderSendResult,
)


class MockNotificationProvider:
    provider_name = "IN_APP_MOCK"

    def validate_connection(self) -> NotificationProviderReadiness:
        return NotificationProviderReadiness(
            provider=self.provider_name,
            status="READY",
            mode="IN_APP_MOCK_ONLY",
            external_calls_enabled=False,
            message="In-app mock notification provider is available. No Email/Kakao/Push/Slack/Webhook calls are performed.",
        )

    def send_message(self, payload: NotificationProviderPayload) -> NotificationProviderSendResult:
        return NotificationProviderSendResult(
            provider=self.provider_name,
            channel=payload.channel,
            delivered=True,
            skipped=False,
            external_calls_enabled=False,
            message="Mock in-app notification dry-run completed without external provider calls.",
        )
