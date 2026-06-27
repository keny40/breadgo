from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.pro_operations_audit import ProOperationsAuditLog
from app.models.user import User
from app.schemas.pro_operations_audit import (
    ProOperationsAuditLogListRead,
    ProOperationsAuditLogPurgePreviewRead,
    ProOperationsAuditLogPurgeResultRead,
    ProOperationsAuditLogRead,
    ProOperationsAuditLogSummaryRead,
)

KST = ZoneInfo("Asia/Seoul")


def create_pro_operation_audit_log(
    db: Session,
    actor: User,
    action_type: str,
    target_type: str,
    status_value: str,
    target_id: UUID | None = None,
    message: str | None = None,
    metadata_json: dict | None = None,
) -> ProOperationsAuditLog:
    audit_log = ProOperationsAuditLog(
        actor_user_id=actor.id,
        actor_role=str(actor.role.value if hasattr(actor.role, "value") else actor.role),
        action_type=action_type,
        target_type=target_type,
        target_id=target_id,
        status=status_value,
        message=message,
        metadata_json=metadata_json or {},
        created_at=datetime.now(timezone.utc),
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log


def _audit_filters(
    action_type: str | None = None,
    status_filter: str | None = None,
    target_type: str | None = None,
    target_id: UUID | None = None,
    actor_user_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list:
    conditions = []
    if action_type:
        conditions.append(ProOperationsAuditLog.action_type == action_type)
    if status_filter:
        if status_filter not in {"SUCCESS", "FAILED"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="status는 SUCCESS 또는 FAILED만 가능합니다.")
        conditions.append(ProOperationsAuditLog.status == status_filter)
    if target_type:
        conditions.append(ProOperationsAuditLog.target_type == target_type)
    if target_id:
        conditions.append(ProOperationsAuditLog.target_id == target_id)
    if actor_user_id:
        conditions.append(ProOperationsAuditLog.actor_user_id == actor_user_id)
    if date_from:
        conditions.append(
            ProOperationsAuditLog.created_at
            >= datetime.combine(date_from, time.min, tzinfo=KST).astimezone(timezone.utc)
        )
    if date_to:
        conditions.append(
            ProOperationsAuditLog.created_at
            < (datetime.combine(date_to, time.min, tzinfo=KST) + timedelta(days=1)).astimezone(timezone.utc)
        )
    return conditions


def list_pro_operation_audit_logs(
    db: Session,
    action_type: str | None = None,
    status_filter: str | None = None,
    target_type: str | None = None,
    target_id: UUID | None = None,
    actor_user_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 50,
    offset: int = 0,
    max_limit: int = 200,
) -> ProOperationsAuditLogListRead:
    bounded_limit = max(1, min(limit, max_limit))
    bounded_offset = max(0, offset)
    conditions = _audit_filters(
        action_type,
        status_filter,
        target_type,
        target_id,
        actor_user_id,
        date_from,
        date_to,
    )
    total_count = db.scalar(select(func.count()).select_from(ProOperationsAuditLog).where(*conditions)) or 0
    logs = list(
        db.scalars(
            select(ProOperationsAuditLog)
            .where(*conditions)
            .order_by(ProOperationsAuditLog.created_at.desc())
            .offset(bounded_offset)
            .limit(bounded_limit)
        )
    )
    return ProOperationsAuditLogListRead(
        audit_logs=[ProOperationsAuditLogRead.model_validate(log) for log in logs],
        total_count=total_count,
    )


def get_pro_operation_audit_log(db: Session, audit_log_id: UUID) -> ProOperationsAuditLogRead:
    audit_log = db.get(ProOperationsAuditLog, audit_log_id)
    if audit_log is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="감사 로그를 찾을 수 없습니다.")
    return ProOperationsAuditLogRead.model_validate(audit_log)


def get_pro_operation_audit_log_summary(
    db: Session,
    action_type: str | None = None,
    status_filter: str | None = None,
    target_type: str | None = None,
    target_id: UUID | None = None,
    actor_user_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> ProOperationsAuditLogSummaryRead:
    logs = list(
        db.scalars(
            select(ProOperationsAuditLog).where(
                *_audit_filters(
                    action_type,
                    status_filter,
                    target_type,
                    target_id,
                    actor_user_id,
                    date_from,
                    date_to,
                )
            )
        )
    )
    last_24h_from = datetime.now(timezone.utc) - timedelta(hours=24)
    latest_action_at = max((log.created_at for log in logs), default=None)
    latest_failed_action_at = max((log.created_at for log in logs if log.status == "FAILED"), default=None)
    action_type_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    for log in logs:
        action_type_counts[log.action_type] = action_type_counts.get(log.action_type, 0) + 1
        status_counts[log.status] = status_counts.get(log.status, 0) + 1
    return ProOperationsAuditLogSummaryRead(
        total_count=len(logs),
        success_count=sum(1 for log in logs if log.status == "SUCCESS"),
        failed_count=sum(1 for log in logs if log.status == "FAILED"),
        latest_action_at=latest_action_at,
        latest_failed_action_at=latest_failed_action_at,
        last_24h_count=sum(1 for log in logs if log.created_at >= last_24h_from),
        last_24h_failed_count=sum(1 for log in logs if log.status == "FAILED" and log.created_at >= last_24h_from),
        action_type_counts=action_type_counts,
        status_counts=status_counts,
    )


def _validate_purge_filters(retention_days: int, status_filter: str | None = None) -> None:
    if retention_days < 30:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="retention_days는 최소 30일 이상이어야 합니다.")
    if status_filter and status_filter not in {"SUCCESS", "FAILED"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="status는 SUCCESS 또는 FAILED만 가능합니다.")


def _audit_purge_cutoff(retention_days: int, date_to: date | None = None) -> datetime:
    if date_to:
        return datetime.combine(date_to, time.min, tzinfo=KST).astimezone(timezone.utc)
    return datetime.now(timezone.utc) - timedelta(days=retention_days)


def _audit_purge_conditions(
    retention_days: int,
    date_to: date | None = None,
    status_filter: str | None = None,
    action_type: str | None = None,
) -> tuple[datetime, list]:
    _validate_purge_filters(retention_days, status_filter)
    cutoff_date = _audit_purge_cutoff(retention_days, date_to)
    conditions = [ProOperationsAuditLog.created_at < cutoff_date]
    if status_filter:
        conditions.append(ProOperationsAuditLog.status == status_filter)
    if action_type:
        conditions.append(ProOperationsAuditLog.action_type == action_type)
    return cutoff_date, conditions


def preview_pro_operation_audit_log_purge(
    db: Session,
    retention_days: int = 180,
    date_to: date | None = None,
    status_filter: str | None = None,
    action_type: str | None = None,
) -> ProOperationsAuditLogPurgePreviewRead:
    cutoff_date, conditions = _audit_purge_conditions(retention_days, date_to, status_filter, action_type)
    logs = list(db.scalars(select(ProOperationsAuditLog).where(*conditions)))
    status_counts: dict[str, int] = {}
    action_type_counts: dict[str, int] = {}
    for log in logs:
        status_counts[log.status] = status_counts.get(log.status, 0) + 1
        action_type_counts[log.action_type] = action_type_counts.get(log.action_type, 0) + 1
    return ProOperationsAuditLogPurgePreviewRead(
        retention_days=retention_days,
        cutoff_date=cutoff_date,
        matched_count=len(logs),
        oldest_created_at=min((log.created_at for log in logs), default=None),
        newest_created_at=max((log.created_at for log in logs), default=None),
        status_counts=status_counts,
        action_type_counts=action_type_counts,
        message=f"{cutoff_date.isoformat()} 이전 감사 로그 {len(logs)}건이 정리 대상입니다.",
    )


def purge_pro_operation_audit_logs(
    db: Session,
    retention_days: int = 180,
    date_to: date | None = None,
    status_filter: str | None = None,
    action_type: str | None = None,
) -> ProOperationsAuditLogPurgeResultRead:
    preview = preview_pro_operation_audit_log_purge(
        db,
        retention_days=retention_days,
        date_to=date_to,
        status_filter=status_filter,
        action_type=action_type,
    )
    cutoff_date, conditions = _audit_purge_conditions(retention_days, date_to, status_filter, action_type)
    result = db.execute(delete(ProOperationsAuditLog).where(*conditions))
    db.commit()
    deleted_count = int(result.rowcount or 0)
    return ProOperationsAuditLogPurgeResultRead(
        retention_days=retention_days,
        cutoff_date=cutoff_date,
        matched_count=preview.matched_count,
        deleted_count=deleted_count,
        oldest_created_at=preview.oldest_created_at,
        newest_created_at=preview.newest_created_at,
        status_counts=preview.status_counts,
        action_type_counts=preview.action_type_counts,
        message=f"오래된 감사 로그 {deleted_count}건을 삭제했습니다.",
    )
