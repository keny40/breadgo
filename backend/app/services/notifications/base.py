from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class NotificationPayload:
    user_id: UUID
    role: str
    title: str
    message: str
    notification_type: str
    related_reservation_id: UUID | None = None
    related_payment_id: UUID | None = None
    related_settlement_id: UUID | None = None


@dataclass(frozen=True)
class NotificationChannelResult:
    channel: str
    delivered: bool
    skipped: bool = False
    message: str | None = None
    external_message_id: str | None = None


class NotificationChannelAdapter:
    channel_name: str

    def send(self, payload: NotificationPayload) -> NotificationChannelResult:
        raise NotImplementedError
