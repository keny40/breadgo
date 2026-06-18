from datetime import datetime

from pydantic import BaseModel


class OpsComponentStatus(BaseModel):
    name: str
    status: str
    message: str | None = None


class OpsStatusResponse(BaseModel):
    app_name: str
    api_version: str
    environment: str
    app_status: str
    checked_at: datetime
    database: OpsComponentStatus
    payment_providers: list[OpsComponentStatus]
    notification_channels: list[OpsComponentStatus]
    incident_notifiers: list[OpsComponentStatus]
