from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReservationHistoryRead(BaseModel):
    id: UUID
    reservation_id: UUID
    actor_user_id: UUID | None = None
    actor_role: str | None = None
    actor_email: str | None = None
    event_type: str
    from_status: str | None = None
    to_status: str | None = None
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
