from app.services.notifications.base import (
    NotificationChannelAdapter,
    NotificationChannelResult,
    NotificationPayload,
)


class EmailNotificationChannel(NotificationChannelAdapter):
    channel_name = "EMAIL"

    def send(self, payload: NotificationPayload) -> NotificationChannelResult:
        return NotificationChannelResult(
            channel=self.channel_name,
            delivered=False,
            skipped=True,
            message="Email notification channel is designed but not enabled in this MVP phase.",
        )
