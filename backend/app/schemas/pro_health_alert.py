from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProHealthAlertRead(BaseModel):
    id: UUID
    severity: str
    status: str
    source: str
    source_key: str
    title: str
    message: str
    created_at: datetime
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ProHealthAlertDetailRead(ProHealthAlertRead):
    details_json: dict | None = None
    acknowledged_by_user_id: UUID | None = None
    resolved_by_user_id: UUID | None = None


class ProHealthAlertListRead(BaseModel):
    alerts: list[ProHealthAlertRead]
    total_count: int


class ProHealthAlertGenerateResultRead(BaseModel):
    generated_count: int
    skipped_count: int
    alerts: list[ProHealthAlertRead]
    message: str


class ProHealthAlertFilters(BaseModel):
    severity: str | None = None
    status: str | None = None
    source: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    limit: int = 50
    offset: int = 0
