from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.services.notifications.base import (
    NotificationChannelAdapter,
    NotificationChannelResult,
    NotificationPayload,
)


class InAppNotificationChannel(NotificationChannelAdapter):
    channel_name = "IN_APP"

    def __init__(self, db: Session) -> None:
        self.db = db
        self.created_notification: Notification | None = None

    def send(self, payload: NotificationPayload) -> NotificationChannelResult:
        notification = Notification(
            user_id=payload.user_id,
            role=payload.role,
            title=payload.title,
            message=payload.message,
            notification_type=payload.notification_type,
            related_reservation_id=payload.related_reservation_id,
            related_payment_id=payload.related_payment_id,
            related_settlement_id=payload.related_settlement_id,
        )
        self.db.add(notification)
        self.created_notification = notification
        return NotificationChannelResult(
            channel=self.channel_name,
            delivered=True,
            message="In-app notification queued.",
            external_message_id=str(notification.id),
        )
