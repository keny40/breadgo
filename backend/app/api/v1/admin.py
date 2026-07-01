import csv
from datetime import date, datetime
from io import StringIO
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import AdminSummary, DemoSeedResponse, MerchantStatusUpdate
from app.schemas.auth import UserResponse
from app.schemas.external_integration import ExternalIntegrationReadinessRead
from app.schemas.merchant import MerchantRead
from app.models.merchant_application import MerchantApplicationStatus
from app.schemas.merchant_application import (
    MerchantApplicationApproveResponse,
    MerchantApplicationRead,
    MerchantApplicationRejectRequest,
)
from app.schemas.payment import PaymentRead
from app.schemas.pro_daily_brief import (
    AdminProOperationsHealthRead,
    AdminProOperationsSummaryRead,
    AdminProWeeklyReportBatchRunMonitorRead,
    AdminProWeeklyReportDeliveryRunHistoryRead,
    AdminProWeeklyReportNotificationListRead,
    AdminProWeeklyReportNotificationSummaryRead,
    AdminWeeklyReportBatchPreviewRead,
    ProWeeklyReportDeliveryRunRead,
    ProWeeklyReportBatchRunRead,
)
from app.schemas.pro_health_alert import (
    ProHealthAlertDetailRead,
    ProHealthAlertGenerateResultRead,
    ProHealthAlertListRead,
)
from app.schemas.pro_operations_audit import (
    ProOperationsAuditLogListRead,
    ProOperationsAuditLogPurgeExecuteRequest,
    ProOperationsAuditLogPurgePreviewRead,
    ProOperationsAuditLogPurgePreviewRequest,
    ProOperationsAuditLogPurgeResultRead,
    ProOperationsAuditLogRead,
    ProOperationsAuditLogSummaryRead,
)
from app.schemas.product import ProductRead
from app.schemas.reservation import DeliveryStatusUpdate, ReservationRead
from app.schemas.reservation_history import ReservationHistoryRead
from app.schemas.store import StoreRead
from app.services.admin_service import (
    get_admin_summary,
    get_merchants,
    get_payments,
    get_products,
    get_reservations,
    get_stores,
    get_users,
    require_admin_user,
    update_merchant_status,
)
from app.services.external_integration_readiness_service import build_external_integration_readiness
from app.services.merchant_application_service import (
    approve_merchant_application,
    get_merchant_application,
    list_merchant_applications,
    reject_merchant_application,
)
from app.services.reservation_service import update_delivery_status_for_admin
from app.services.reservation_history_service import get_history_for_admin
from app.services.pro_daily_brief_service import (
    build_admin_pro_operations_health,
    build_admin_pro_operations_summary,
    create_admin_weekly_report_batch_run,
    create_weekly_report_in_app_mock_delivery,
    create_weekly_report_delivery_preview,
    create_weekly_report_unread_reminders,
    get_admin_weekly_report_batch_run,
    get_admin_weekly_report_notification_summary,
    get_weekly_report_delivery_run,
    list_admin_weekly_report_notifications,
    list_weekly_report_delivery_runs,
    list_admin_weekly_report_batch_runs,
    preview_admin_weekly_report_batch_run,
    retry_failed_weekly_report_batch_items,
)
from app.services.pro_operations_audit_service import (
    create_pro_operation_audit_log,
    get_pro_operation_audit_log,
    get_pro_operation_audit_log_summary,
    list_pro_operation_audit_logs,
    preview_pro_operation_audit_log_purge,
    purge_pro_operation_audit_logs,
)
from app.services.pro_health_alert_service import (
    acknowledge_pro_health_alert,
    generate_pro_health_alerts,
    get_pro_health_alert,
    list_pro_health_alerts,
    resolve_pro_health_alert,
)
from app.api.v1.reservations import reservation_history_to_read, reservation_to_read
from scripts.seed_demo import seed_demo_data


router = APIRouter()


def _safe_audit_failure(db: Session, actor: User, action_type: str, target_type: str, message: str) -> None:
    try:
        db.rollback()
        create_pro_operation_audit_log(
            db,
            actor=actor,
            action_type=action_type,
            target_type=target_type,
            status_value="FAILED",
            message=message[:500],
        )
    except Exception:
        db.rollback()


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    return require_admin_user(current_user)


@router.get("/summary", response_model=AdminSummary)
def get_summary(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminSummary:
    return get_admin_summary(db)


@router.get("/users", response_model=list[UserResponse])
def list_users(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    return [UserResponse.model_validate(user) for user in get_users(db)]


@router.get("/merchants", response_model=list[MerchantRead])
def list_merchants(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[MerchantRead]:
    return [MerchantRead.model_validate(merchant) for merchant in get_merchants(db)]


@router.get("/stores", response_model=list[StoreRead])
def list_stores(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[StoreRead]:
    return [StoreRead.model_validate(store) for store in get_stores(db)]


@router.get("/products", response_model=list[ProductRead])
def list_products(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[ProductRead]:
    return [ProductRead.model_validate(product) for product in get_products(db)]


@router.get("/reservations", response_model=list[ReservationRead])
def list_reservations(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[ReservationRead]:
    return [ReservationRead.model_validate(reservation) for reservation in get_reservations(db)]


@router.patch("/reservations/{reservation_id}/delivery-status", response_model=ReservationRead)
def change_reservation_delivery_status(
    reservation_id: UUID,
    payload: DeliveryStatusUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ReservationRead:
    reservation = update_delivery_status_for_admin(db, reservation_id, payload, current_admin)
    return reservation_to_read(reservation)


@router.get("/reservations/{reservation_id}/history", response_model=list[ReservationHistoryRead])
def get_admin_reservation_history(
    reservation_id: UUID,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[ReservationHistoryRead]:
    events = get_history_for_admin(db, reservation_id)
    return [reservation_history_to_read(event) for event in events]


@router.get("/payments", response_model=list[PaymentRead])
def list_payments(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[PaymentRead]:
    return [PaymentRead.model_validate(payment) for payment in get_payments(db)]


@router.patch("/merchants/{merchant_id}/status", response_model=MerchantRead)
def change_merchant_status(
    merchant_id: UUID,
    payload: MerchantStatusUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> MerchantRead:
    merchant = update_merchant_status(db, merchant_id, payload)
    return MerchantRead.model_validate(merchant)


@router.get("/merchant-applications", response_model=list[MerchantApplicationRead])
def list_admin_merchant_applications(
    status_filter: MerchantApplicationStatus | None = Query(default=None, alias="status"),
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[MerchantApplicationRead]:
    applications = list_merchant_applications(db, status_filter)
    return [MerchantApplicationRead.model_validate(application) for application in applications]


@router.get("/merchant-applications/{application_id}", response_model=MerchantApplicationRead)
def get_admin_merchant_application(
    application_id: UUID,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> MerchantApplicationRead:
    application = get_merchant_application(db, application_id)
    return MerchantApplicationRead.model_validate(application)


@router.post("/merchant-applications/{application_id}/approve", response_model=MerchantApplicationApproveResponse)
def approve_admin_merchant_application(
    application_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> MerchantApplicationApproveResponse:
    application, merchant = approve_merchant_application(db, application_id, current_admin)
    return MerchantApplicationApproveResponse(
        application=MerchantApplicationRead.model_validate(application),
        merchant=MerchantRead.model_validate(merchant),
    )


@router.post("/merchant-applications/{application_id}/reject", response_model=MerchantApplicationRead)
def reject_admin_merchant_application(
    application_id: UUID,
    payload: MerchantApplicationRejectRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> MerchantApplicationRead:
    application = reject_merchant_application(db, application_id, payload, current_admin)
    return MerchantApplicationRead.model_validate(application)


@router.post("/demo/seed", response_model=DemoSeedResponse)
def seed_demo(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> DemoSeedResponse:
    return DemoSeedResponse(**seed_demo_data(db))


@router.get("/pro/operations/summary", response_model=AdminProOperationsSummaryRead)
def get_admin_pro_operations_summary(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminProOperationsSummaryRead:
    return build_admin_pro_operations_summary(db)


@router.get("/pro/operations/health", response_model=AdminProOperationsHealthRead)
def get_admin_pro_operations_health(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminProOperationsHealthRead:
    return build_admin_pro_operations_health(db)


@router.get("/pro/operations/external-integrations/readiness", response_model=ExternalIntegrationReadinessRead)
def get_admin_external_integration_readiness(
    _: User = Depends(get_current_admin),
) -> ExternalIntegrationReadinessRead:
    return ExternalIntegrationReadinessRead.model_validate(build_external_integration_readiness())


@router.post("/pro/operations/health/alerts/generate", response_model=ProHealthAlertGenerateResultRead)
def generate_admin_pro_health_alerts(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProHealthAlertGenerateResultRead:
    try:
        health = build_admin_pro_operations_health(db)
        result = generate_pro_health_alerts(db, health)
        create_pro_operation_audit_log(
            db,
            actor=current_admin,
            action_type="GENERATE_HEALTH_ALERTS",
            target_type="HEALTH_ALERT",
            status_value="SUCCESS",
            message="Pro Operations Health Alert를 생성했습니다.",
            metadata_json={
                "generated_count": result.generated_count,
                "skipped_count": result.skipped_count,
                "overall_status": health.overall_status,
            },
        )
        return result
    except Exception as exc:
        _safe_audit_failure(db, current_admin, "GENERATE_HEALTH_ALERTS", "HEALTH_ALERT", str(exc))
        raise


@router.get("/pro/operations/health/alerts", response_model=ProHealthAlertListRead)
def list_admin_pro_health_alerts(
    severity: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    source: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 50,
    offset: int = 0,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProHealthAlertListRead:
    return list_pro_health_alerts(
        db,
        severity=severity,
        status_filter=status_filter,
        source=source,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )


@router.post("/pro/operations/health/alerts/{alert_id}/acknowledge", response_model=ProHealthAlertDetailRead)
def acknowledge_admin_pro_health_alert(
    alert_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProHealthAlertDetailRead:
    try:
        result = acknowledge_pro_health_alert(db, alert_id, current_admin)
        create_pro_operation_audit_log(
            db,
            actor=current_admin,
            action_type="ACKNOWLEDGE_HEALTH_ALERT",
            target_type="HEALTH_ALERT",
            target_id=result.id,
            status_value="SUCCESS",
            message="Pro Health Alert를 확인 처리했습니다.",
            metadata_json={"alert_id": str(result.id), "severity": result.severity, "status": result.status},
        )
        return result
    except Exception as exc:
        _safe_audit_failure(db, current_admin, "ACKNOWLEDGE_HEALTH_ALERT", "HEALTH_ALERT", str(exc))
        raise


@router.post("/pro/operations/health/alerts/{alert_id}/resolve", response_model=ProHealthAlertDetailRead)
def resolve_admin_pro_health_alert(
    alert_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProHealthAlertDetailRead:
    try:
        result = resolve_pro_health_alert(db, alert_id, current_admin)
        create_pro_operation_audit_log(
            db,
            actor=current_admin,
            action_type="RESOLVE_HEALTH_ALERT",
            target_type="HEALTH_ALERT",
            target_id=result.id,
            status_value="SUCCESS",
            message="Pro Health Alert를 해결 처리했습니다.",
            metadata_json={"alert_id": str(result.id), "severity": result.severity, "status": result.status},
        )
        return result
    except Exception as exc:
        _safe_audit_failure(db, current_admin, "RESOLVE_HEALTH_ALERT", "HEALTH_ALERT", str(exc))
        raise


@router.get("/pro/operations/health/alerts/{alert_id}", response_model=ProHealthAlertDetailRead)
def get_admin_pro_health_alert(
    alert_id: UUID,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProHealthAlertDetailRead:
    return get_pro_health_alert(db, alert_id)


@router.get("/pro/operations/audit-logs/summary", response_model=ProOperationsAuditLogSummaryRead)
def get_admin_pro_operations_audit_log_summary(
    action_type: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    target_type: str | None = None,
    target_id: UUID | None = None,
    actor_user_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProOperationsAuditLogSummaryRead:
    return get_pro_operation_audit_log_summary(
        db,
        action_type=action_type,
        status_filter=status_filter,
        target_type=target_type,
        target_id=target_id,
        actor_user_id=actor_user_id,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/pro/operations/audit-logs/export.csv")
def export_admin_pro_operations_audit_logs_csv(
    action_type: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    target_type: str | None = None,
    target_id: UUID | None = None,
    actor_user_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> Response:
    try:
        result = list_pro_operation_audit_logs(
            db,
            action_type=action_type,
            status_filter=status_filter,
            target_type=target_type,
            target_id=target_id,
            actor_user_id=actor_user_id,
            date_from=date_from,
            date_to=date_to,
            limit=10000,
            offset=0,
            max_limit=10000,
        )

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "id",
                "created_at",
                "actor_user_id",
                "actor_role",
                "action_type",
                "target_type",
                "target_id",
                "status",
                "message",
            ]
        )
        for log in result.audit_logs:
            writer.writerow(
                [
                    str(log.id),
                    log.created_at.isoformat(),
                    str(log.actor_user_id) if log.actor_user_id else "",
                    log.actor_role,
                    log.action_type,
                    log.target_type,
                    str(log.target_id) if log.target_id else "",
                    log.status,
                    log.message or "",
                ]
            )

        create_pro_operation_audit_log(
            db,
            actor=current_admin,
            action_type="EXPORT_AUDIT_LOG_CSV",
            target_type="AUDIT_LOG",
            status_value="SUCCESS",
            message="Pro Operations Audit Log CSV를 다운로드했습니다.",
            metadata_json={
                "filters": {
                    "action_type": action_type,
                    "status": status_filter,
                    "target_type": target_type,
                    "target_id": str(target_id) if target_id else None,
                    "actor_user_id": str(actor_user_id) if actor_user_id else None,
                    "date_from": date_from.isoformat() if date_from else None,
                    "date_to": date_to.isoformat() if date_to else None,
                },
                "exported_count": len(result.audit_logs),
            },
        )

        filename = f"pro-audit-logs-{datetime.now().strftime('%Y%m%d')}.csv"
        return Response(
            content="\ufeff" + output.getvalue(),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        _safe_audit_failure(db, current_admin, "EXPORT_AUDIT_LOG_CSV", "AUDIT_LOG", str(exc))
        raise


@router.post("/pro/operations/audit-logs/purge/preview", response_model=ProOperationsAuditLogPurgePreviewRead)
def preview_admin_pro_operations_audit_log_purge(
    payload: ProOperationsAuditLogPurgePreviewRequest,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProOperationsAuditLogPurgePreviewRead:
    return preview_pro_operation_audit_log_purge(
        db,
        retention_days=payload.retention_days,
        date_to=payload.date_to,
        status_filter=payload.status,
        action_type=payload.action_type,
    )


@router.post("/pro/operations/audit-logs/purge", response_model=ProOperationsAuditLogPurgeResultRead)
def purge_admin_pro_operations_audit_logs(
    payload: ProOperationsAuditLogPurgeExecuteRequest,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProOperationsAuditLogPurgeResultRead:
    if not payload.confirm:
        raise HTTPException(status_code=400, detail="감사 로그 삭제를 실행하려면 confirm=true가 필요합니다.")
    try:
        result = purge_pro_operation_audit_logs(
            db,
            retention_days=payload.retention_days,
            date_to=payload.date_to,
            status_filter=payload.status,
            action_type=payload.action_type,
        )
        create_pro_operation_audit_log(
            db,
            actor=current_admin,
            action_type="PURGE_AUDIT_LOGS",
            target_type="AUDIT_LOG",
            status_value="SUCCESS",
            message="오래된 Pro Operations Audit Log를 삭제했습니다.",
            metadata_json={
                "retention_days": payload.retention_days,
                "cutoff_date": result.cutoff_date.isoformat(),
                "deleted_count": result.deleted_count,
                "filter_status": payload.status,
                "filter_action_type": payload.action_type,
            },
        )
        return result
    except Exception as exc:
        _safe_audit_failure(db, current_admin, "PURGE_AUDIT_LOGS", "AUDIT_LOG", str(exc))
        raise


@router.get("/pro/operations/audit-logs/{audit_log_id}", response_model=ProOperationsAuditLogRead)
def get_admin_pro_operations_audit_log(
    audit_log_id: UUID,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProOperationsAuditLogRead:
    return get_pro_operation_audit_log(db, audit_log_id)


@router.get("/pro/operations/audit-logs", response_model=ProOperationsAuditLogListRead)
def list_admin_pro_operations_audit_logs(
    action_type: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    target_type: str | None = None,
    target_id: UUID | None = None,
    actor_user_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 50,
    offset: int = 0,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProOperationsAuditLogListRead:
    return list_pro_operation_audit_logs(
        db,
        action_type=action_type,
        status_filter=status_filter,
        target_type=target_type,
        target_id=target_id,
        actor_user_id=actor_user_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )


@router.post("/pro/weekly-report/delivery-runs/preview", response_model=ProWeeklyReportDeliveryRunRead)
def create_weekly_report_delivery_preview_for_admin(
    start_date: date | None = None,
    end_date: date | None = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProWeeklyReportDeliveryRunRead:
    try:
        result = create_weekly_report_delivery_preview(db, start_date=start_date, end_date=end_date)
        create_pro_operation_audit_log(
            db,
            actor=current_admin,
            action_type="CREATE_DELIVERY_PREVIEW",
            target_type="DELIVERY_RUN",
            target_id=result.id,
            status_value="SUCCESS",
            message="Weekly Report delivery preview를 생성했습니다.",
            metadata_json={
                "run_id": str(result.id),
                "status": result.status,
                "ready_count": result.ready_count,
                "skipped_count": result.skipped_count,
                "failed_count": result.failed_count,
            },
        )
        return result
    except Exception as exc:
        _safe_audit_failure(db, current_admin, "CREATE_DELIVERY_PREVIEW", "DELIVERY_RUN", str(exc))
        raise


@router.get("/pro/weekly-report/delivery-runs", response_model=AdminProWeeklyReportDeliveryRunHistoryRead)
def list_weekly_report_delivery_runs_for_admin(
    limit: int = 50,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminProWeeklyReportDeliveryRunHistoryRead:
    return list_weekly_report_delivery_runs(db, limit=limit)


@router.get("/pro/weekly-report/delivery-runs/{delivery_run_id}", response_model=ProWeeklyReportDeliveryRunRead)
def get_weekly_report_delivery_run_for_admin(
    delivery_run_id: UUID,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProWeeklyReportDeliveryRunRead:
    return get_weekly_report_delivery_run(db, delivery_run_id)


@router.get("/pro/weekly-report/notifications/summary", response_model=AdminProWeeklyReportNotificationSummaryRead)
def get_weekly_report_notification_summary_for_admin(
    merchant_id: UUID | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    date_from: date | None = None,
    date_to: date | None = None,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminProWeeklyReportNotificationSummaryRead:
    return get_admin_weekly_report_notification_summary(
        db,
        merchant_id=merchant_id,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/pro/weekly-report/notifications", response_model=AdminProWeeklyReportNotificationListRead)
def list_weekly_report_notifications_for_admin(
    merchant_id: UUID | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 100,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminProWeeklyReportNotificationListRead:
    return list_admin_weekly_report_notifications(
        db,
        merchant_id=merchant_id,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )


@router.post(
    "/pro/weekly-report/delivery-runs/{delivery_run_id}/mock-send",
    response_model=ProWeeklyReportDeliveryRunRead,
)
def create_weekly_report_in_app_mock_delivery_for_admin(
    delivery_run_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProWeeklyReportDeliveryRunRead:
    try:
        result = create_weekly_report_in_app_mock_delivery(db, delivery_run_id)
        create_pro_operation_audit_log(
            db,
            actor=current_admin,
            action_type="RUN_IN_APP_MOCK_DELIVERY",
            target_type="DELIVERY_RUN",
            target_id=result.id,
            status_value="SUCCESS",
            message="Weekly Report in-app mock delivery를 실행했습니다.",
            metadata_json={
                "source_delivery_run_id": str(delivery_run_id),
                "run_id": str(result.id),
                "status": result.status,
                "sent_count": result.ready_count,
                "skipped_count": result.skipped_count,
                "failed_count": result.failed_count,
            },
        )
        return result
    except Exception as exc:
        _safe_audit_failure(db, current_admin, "RUN_IN_APP_MOCK_DELIVERY", "DELIVERY_RUN", str(exc))
        raise


@router.post("/pro/weekly-report/notifications/remind-unread", response_model=ProWeeklyReportDeliveryRunRead)
def create_weekly_report_unread_reminders_for_admin(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProWeeklyReportDeliveryRunRead:
    try:
        result = create_weekly_report_unread_reminders(db)
        create_pro_operation_audit_log(
            db,
            actor=current_admin,
            action_type="RUN_UNREAD_REMINDER",
            target_type="NOTIFICATION",
            target_id=result.id,
            status_value="SUCCESS",
            message="미확인 Weekly Report 알림 리마인드를 실행했습니다.",
            metadata_json={
                "delivery_run_id": str(result.id),
                "status": result.status,
                "sent_count": result.ready_count,
                "skipped_count": result.skipped_count,
                "failed_count": result.failed_count,
            },
        )
        return result
    except Exception as exc:
        _safe_audit_failure(db, current_admin, "RUN_UNREAD_REMINDER", "NOTIFICATION", str(exc))
        raise


@router.get("/pro/weekly-report/batch-runs", response_model=AdminProWeeklyReportBatchRunMonitorRead)
def list_weekly_report_batch_runs_for_admin(
    status_filter: str | None = Query(default=None, alias="status"),
    run_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 50,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminProWeeklyReportBatchRunMonitorRead:
    return list_admin_weekly_report_batch_runs(
        db,
        status_filter=status_filter,
        run_type=run_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )


@router.post("/pro/weekly-report/batch-runs/preview", response_model=AdminWeeklyReportBatchPreviewRead)
def preview_weekly_report_batch_run_for_admin(
    start_date: date | None = None,
    end_date: date | None = None,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminWeeklyReportBatchPreviewRead:
    return preview_admin_weekly_report_batch_run(db, start_date=start_date, end_date=end_date)


@router.post("/pro/weekly-report/batch-runs", response_model=ProWeeklyReportBatchRunRead)
def create_weekly_report_batch_run_for_admin(
    start_date: date | None = None,
    end_date: date | None = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProWeeklyReportBatchRunRead:
    try:
        result = create_admin_weekly_report_batch_run(db, start_date=start_date, end_date=end_date)
        create_pro_operation_audit_log(
            db,
            actor=current_admin,
            action_type="RUN_WEEKLY_REPORT_BATCH",
            target_type="BATCH_RUN",
            target_id=result.id,
            status_value="SUCCESS",
            message="전체 Weekly Report batch를 실행했습니다.",
            metadata_json={
                "batch_run_id": str(result.id),
                "status": result.status,
                "success_count": result.success_count,
                "failed_count": result.failed_count,
                "skipped_count": result.skipped_count,
            },
        )
        return result
    except Exception as exc:
        _safe_audit_failure(db, current_admin, "RUN_WEEKLY_REPORT_BATCH", "BATCH_RUN", str(exc))
        raise


@router.post("/pro/weekly-report/batch-runs/{batch_run_id}/retry-failed", response_model=ProWeeklyReportBatchRunRead)
def retry_failed_weekly_report_batch_items_for_admin(
    batch_run_id: UUID,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProWeeklyReportBatchRunRead:
    try:
        result = retry_failed_weekly_report_batch_items(db, batch_run_id)
        create_pro_operation_audit_log(
            db,
            actor=current_admin,
            action_type="RETRY_FAILED_BATCH_ITEMS",
            target_type="BATCH_RUN",
            target_id=result.id,
            status_value="SUCCESS",
            message="Weekly Report 실패 batch item 재실행을 완료했습니다.",
            metadata_json={
                "source_batch_run_id": str(batch_run_id),
                "retry_batch_run_id": str(result.id),
                "status": result.status,
                "success_count": result.success_count,
                "failed_count": result.failed_count,
            },
        )
        return result
    except Exception as exc:
        _safe_audit_failure(db, current_admin, "RETRY_FAILED_BATCH_ITEMS", "BATCH_RUN", str(exc))
        raise


@router.get("/pro/weekly-report/batch-runs/{batch_run_id}", response_model=ProWeeklyReportBatchRunRead)
def get_weekly_report_batch_run_for_admin(
    batch_run_id: UUID,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProWeeklyReportBatchRunRead:
    return get_admin_weekly_report_batch_run(db, batch_run_id)
