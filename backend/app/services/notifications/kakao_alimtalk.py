from app.services.notifications.base import (
    NotificationChannelAdapter,
    NotificationChannelResult,
    NotificationPayload,
)


class KakaoAlimtalkNotificationChannel(NotificationChannelAdapter):
    channel_name = "KAKAO_ALIMTALK"

    def send(self, payload: NotificationPayload) -> NotificationChannelResult:
        return NotificationChannelResult(
            channel=self.channel_name,
            delivered=False,
            skipped=True,
            message="Kakao Alimtalk notification channel is designed but not enabled in this MVP phase.",
        )
