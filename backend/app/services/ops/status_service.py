from datetime import datetime, timezone
import os

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.ops import OpsComponentStatus, OpsStatusResponse


logger = get_logger("ops.status")


def _database_status(db: Session) -> OpsComponentStatus:
    try:
        db.execute(text("SELECT 1"))
        return OpsComponentStatus(name="PostgreSQL", status="ok", message="Database connection is healthy.")
    except Exception as exc:
        logger.exception("Database health check failed.")
        return OpsComponentStatus(name="PostgreSQL", status="error", message=exc.__class__.__name__)


def build_ops_status(db: Session) -> OpsStatusResponse:
    database = _database_status(db)
    app_status = "ok" if database.status == "ok" else "degraded"

    return OpsStatusResponse(
        app_name=settings.PROJECT_NAME,
        api_version=settings.API_VERSION,
        environment=os.getenv("ENVIRONMENT", "local"),
        app_status=app_status,
        checked_at=datetime.now(timezone.utc),
        database=database,
        payment_providers=[
            OpsComponentStatus(name="MOCK", status="enabled", message="MVP mock payment provider is active."),
            OpsComponentStatus(name="TOSS", status="skeleton", message="Designed but external API is not connected."),
            OpsComponentStatus(name="KAKAO_PAY", status="planned", message="Provider expansion target."),
            OpsComponentStatus(name="NAVER_PAY", status="planned", message="Provider expansion target."),
        ],
        notification_channels=[
            OpsComponentStatus(name="IN_APP", status="enabled", message="In-app notification channel is active."),
            OpsComponentStatus(name="EMAIL", status="skeleton", message="Designed but external API is not connected."),
            OpsComponentStatus(name="SMS", status="skeleton", message="Designed but external API is not connected."),
            OpsComponentStatus(name="KAKAO_ALIMTALK", status="skeleton", message="Designed but external API is not connected."),
            OpsComponentStatus(name="PUSH", status="skeleton", message="Designed but external API is not connected."),
        ],
        incident_notifiers=[
            OpsComponentStatus(name="LOG", status="enabled", message="Incidents can be written to application logs."),
            OpsComponentStatus(name="SLACK", status="skeleton", message="Designed but external webhook is not configured."),
            OpsComponentStatus(name="SENTRY", status="skeleton", message="Designed but external DSN is not configured."),
        ],
    )
