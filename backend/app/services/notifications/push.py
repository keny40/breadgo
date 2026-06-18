from app.services.notifications.base import (
    NotificationChannelAdapter,
    NotificationChannelResult,
    NotificationPayload,
)


class PushNotificationChannel(NotificationChannelAdapter):
    channel_name = "PUSH"

    def send(self, payload: NotificationPayload) -> NotificationChannelResult:
        return NotificationChannelResult(
            channel=self.channel_name,
            delivered=False,
            skipped=True,
            message="Push notification channel is designed but not enabled in this MVP phase.",
        )
