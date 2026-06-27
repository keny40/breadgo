from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.pro_health_alert import ProHealthAlert
from app.models.user import User
from app.schemas.pro_daily_brief import AdminProOperationsHealthItemRead, AdminProOperationsHealthRead
from app.schemas.pro_health_alert import (
    ProHealthAlertDetailRead,
    ProHealthAlertGenerateResultRead,
    ProHealthAlertListRead,
    ProHealthAlertRead,
)

KST = ZoneInfo("Asia/Seoul")
ACTIVE_ALERT_STATUSES = {"OPEN", "ACKNOWLEDGED"}
VALID_ALERT_SEVERITIES = {"WARNING", "CRITICAL"}
VALID_ALERT_STATUSES = {"OPEN", "ACKNOWLEDGED", "RESOLVED"}


def _safe_details(details: dict) -> dict:
    allowed: dict = {}
    for key, value in details.items():
        lowered = str(key).lower()
        if any(blocked in lowered for blocked in ["email", "phone", "address", "token"]):
            continue
        allowed[key] = value
    return allowed


def _alert_filters(
    severity: str | None = None,
    status_filter: str | None = None,
    source: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list:
    conditions = []
    if severity:
        if severity not in VALID_ALERT_SEVERITIES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="severity는 WARNING 또는 CRITICAL만 가능합니다.")
        conditions.append(ProHealthAlert.severity == severity)
    if status_filter:
        if status_filter not in VALID_ALERT_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="status는 OPEN, ACKNOWLEDGED, RESOLVED만 가능합니다.",
            )
        conditions.append(ProHealthAlert.status == status_filter)
    if source:
        conditions.append(ProHealthAlert.source == source)
    if date_from:
        conditions.append(
            ProHealthAlert.created_at >= datetime.combine(date_from, time.min, tzinfo=KST).astimezone(timezone.utc)
        )
    if date_to:
        conditions.append(
            ProHealthAlert.created_at
            < (datetime.combine(date_to, time.min, tzinfo=KST) + timedelta(days=1)).astimezone(timezone.utc)
        )
    return conditions


def _health_alert_title(label: str, item: AdminProOperationsHealthItemRead) -> str:
    return f"{label} 상태 {item.status}"


def _health_alert_source_key(key: str, item: AdminProOperationsHealthItemRead) -> str:
    return f"{key}:{item.status}"


def _health_alert_candidates(health: AdminProOperationsHealthRead) -> list[tuple[str, str, AdminProOperationsHealthItemRead]]:
    return [
        ("scheduler", "Scheduler", health.scheduler_health),
        ("batch", "Batch", health.batch_health),
        ("delivery", "Delivery", health.delivery_health),
        ("notification", "Notification", health.notification_health),
        ("audit_log", "Audit Log", health.audit_log_health),
        ("purge_policy", "Purge Policy", health.purge_policy_health),
    ]


def generate_pro_health_alerts(db: Session, health: AdminProOperationsHealthRead) -> ProHealthAlertGenerateResultRead:
    generated: list[ProHealthAlert] = []
    skipped_count = 0
    for key, label, item in _health_alert_candidates(health):
        if item.status not in VALID_ALERT_SEVERITIES:
            continue
        source_key = _health_alert_source_key(key, item)
        existing = db.scalar(
            select(ProHealthAlert).where(
                ProHealthAlert.source == "HEALTH_CHECK",
                ProHealthAlert.source_key == source_key,
                ProHealthAlert.status.in_(ACTIVE_ALERT_STATUSES),
            )
        )
        if existing is not None:
            skipped_count += 1
            continue
        alert = ProHealthAlert(
            severity=item.status,
            status="OPEN",
            source="HEALTH_CHECK",
            source_key=source_key,
            title=_health_alert_title(label, item),
            message=item.message,
            details_json=_safe_details(item.details),
            created_at=datetime.now(timezone.utc),
        )
        db.add(alert)
        generated.append(alert)
    db.commit()
    for alert in generated:
        db.refresh(alert)
    return ProHealthAlertGenerateResultRead(
        generated_count=len(generated),
        skipped_count=skipped_count,
        alerts=[ProHealthAlertRead.model_validate(alert) for alert in generated],
        message=f"Health alert {len(generated)}건 생성, {skipped_count}건 중복 skip 처리했습니다.",
    )


def list_pro_health_alerts(
    db: Session,
    severity: str | None = None,
    status_filter: str | None = None,
    source: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 50,
    offset: int = 0,
) -> ProHealthAlertListRead:
    bounded_limit = max(1, min(limit, 200))
    bounded_offset = max(0, offset)
    conditions = _alert_filters(severity, status_filter, source, date_from, date_to)
    total_count = db.scalar(select(func.count()).select_from(ProHealthAlert).where(*conditions)) or 0
    alerts = list(
        db.scalars(
            select(ProHealthAlert)
            .where(*conditions)
            .order_by(ProHealthAlert.created_at.desc())
            .offset(bounded_offset)
            .limit(bounded_limit)
        )
    )
    return ProHealthAlertListRead(
        alerts=[ProHealthAlertRead.model_validate(alert) for alert in alerts],
        total_count=total_count,
    )


def get_pro_health_alert(db: Session, alert_id: UUID) -> ProHealthAlertDetailRead:
    alert = db.get(ProHealthAlert, alert_id)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health alert를 찾을 수 없습니다.")
    return ProHealthAlertDetailRead.model_validate(alert)


def acknowledge_pro_health_alert(db: Session, alert_id: UUID, actor: User) -> ProHealthAlertDetailRead:
    alert = db.get(ProHealthAlert, alert_id)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health alert를 찾을 수 없습니다.")
    if alert.status == "RESOLVED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 해결된 Health alert입니다.")
    if alert.status == "OPEN":
        alert.status = "ACKNOWLEDGED"
        alert.acknowledged_at = datetime.now(timezone.utc)
        alert.acknowledged_by_user_id = actor.id
        db.commit()
        db.refresh(alert)
    return ProHealthAlertDetailRead.model_validate(alert)


def resolve_pro_health_alert(db: Session, alert_id: UUID, actor: User) -> ProHealthAlertDetailRead:
    alert = db.get(ProHealthAlert, alert_id)
    if alert is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Health alert를 찾을 수 없습니다.")
    if alert.status == "RESOLVED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 해결된 Health alert입니다.")
    alert.status = "RESOLVED"
    alert.resolved_at = datetime.now(timezone.utc)
    alert.resolved_by_user_id = actor.id
    db.commit()
    db.refresh(alert)
    return ProHealthAlertDetailRead.model_validate(alert)
