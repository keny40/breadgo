from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProOperationsAuditLogRead(BaseModel):
    id: UUID
    actor_user_id: UUID | None = None
    actor_role: str
    action_type: str
    target_type: str
    target_id: UUID | None = None
    status: str
    message: str | None = None
    metadata_json: dict | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProOperationsAuditLogListRead(BaseModel):
    audit_logs: list[ProOperationsAuditLogRead]
    total_count: int


class ProOperationsAuditLogSummaryRead(BaseModel):
    total_count: int
    success_count: int
    failed_count: int
    latest_action_at: datetime | None = None
    latest_failed_action_at: datetime | None = None
    last_24h_count: int
    last_24h_failed_count: int
    action_type_counts: dict[str, int]
    status_counts: dict[str, int]


class ProOperationsAuditLogFilters(BaseModel):
    action_type: str | None = None
    status: str | None = None
    target_type: str | None = None
    target_id: UUID | None = None
    actor_user_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None


class ProOperationsAuditLogPurgePreviewRequest(BaseModel):
    retention_days: int = 180
    date_to: date | None = None
    status: str | None = None
    action_type: str | None = None


class ProOperationsAuditLogPurgeExecuteRequest(ProOperationsAuditLogPurgePreviewRequest):
    confirm: bool = False


class ProOperationsAuditLogPurgePreviewRead(BaseModel):
    retention_days: int
    cutoff_date: datetime
    matched_count: int
    oldest_created_at: datetime | None = None
    newest_created_at: datetime | None = None
    status_counts: dict[str, int]
    action_type_counts: dict[str, int]
    message: str


class ProOperationsAuditLogPurgeResultRead(ProOperationsAuditLogPurgePreviewRead):
    deleted_count: int
