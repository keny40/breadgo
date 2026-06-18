from app.services.notifications.base import (
    NotificationChannelAdapter,
    NotificationChannelResult,
    NotificationPayload,
)


class SmsNotificationChannel(NotificationChannelAdapter):
    channel_name = "SMS"

    def send(self, payload: NotificationPayload) -> NotificationChannelResult:
        return NotificationChannelResult(
            channel=self.channel_name,
            delivered=False,
            skipped=True,
            message="SMS notification channel is designed but not enabled in this MVP phase.",
        )
