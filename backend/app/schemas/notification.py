from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    id: UUID
    user_id: UUID
    role: str
    title: str
    message: str
    notification_type: str
    related_reservation_id: UUID | None = None
    related_payment_id: UUID | None = None
    related_settlement_id: UUID | None = None
    is_read: bool
    created_at: datetime
    read_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
