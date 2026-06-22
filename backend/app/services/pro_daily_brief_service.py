from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.merchant import Merchant
from app.models.pro_daily_brief import ProDailyBriefSnapshot, ProDailyBriefTask
from app.models.product_import import ProductImportBatch
from app.models.product_inventory_event import ProductInventoryEvent
from app.schemas.pro_daily_brief import (
    MerchantProDailyBriefHistoryRead,
    MerchantProDailyBriefRead,
    ProDailyBriefHistoryDeltaRead,
    ProDailyBriefSnapshotRead,
    ProDailyBriefTaskRead,
)
from app.schemas.pro_inventory_alert import ProInventoryAlertRead
from app.schemas.pro_recommendation import ProRecommendationRead
from app.services.pos_integration_service import get_or_create_pos_integration
from app.services.pro_dashboard_service import build_merchant_pro_dashboard
from app.services.pro_inventory_alert_service import build_merchant_pro_inventory_alerts
from app.services.pro_recommendation_service import build_merchant_pro_recommendations

KST = ZoneInfo("Asia/Seoul")
RESOLVED_ACTIONS = {"MARKED_RESOLVED", "DISMISSED"}
PRIORITY_RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def _today_window() -> tuple[datetime, datetime]:
    now = datetime.now(KST)
    start = datetime.combine(now.date(), time.min, tzinfo=KST)
    end = start + timedelta(days=1)
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def _is_unresolved(alert: ProInventoryAlertRead) -> bool:
    return not alert.is_resolved and alert.latest_action_type not in RESOLVED_ACTIONS


def _priority_key(value: str) -> int:
    return PRIORITY_RANK.get(value, 3)


def _alert_task(alert: ProInventoryAlertRead) -> ProDailyBriefTaskRead:
    task_type = "LOW_STOCK_HIGH_DEMAND" if alert.alert_type == "LOW_STOCK_HIGH_DEMAND" else "INVENTORY_ALERT"
    return ProDailyBriefTaskRead(
        task_type=task_type,
        priority=alert.severity,
        title=alert.title,
        message=f"{alert.product_name}: {alert.message}",
        action_label="재고 알림 확인",
        action_href="/merchant/pro/inventory-alerts",
    )


def _recommendation_task(recommendation: ProRecommendationRead) -> ProDailyBriefTaskRead:
    reasons = " ".join(recommendation.explanation_reasons[:2])
    message = reasons or recommendation.recommendation_message
    return ProDailyBriefTaskRead(
        task_type="RECOMMENDATION_ACTION",
        priority=recommendation.action_priority,
        title=f"{recommendation.product_name} 추천 액션",
        message=message,
        action_label=recommendation.primary_action_label or "추천 확인",
        action_href="/merchant/pro/recommendations",
    )


def _count_today_inventory_events(db: Session, merchant: Merchant, start: datetime, end: datetime) -> int:
    return int(
        db.scalar(
            select(func.count(ProductInventoryEvent.id)).where(
                ProductInventoryEvent.merchant_id == merchant.id,
                ProductInventoryEvent.created_at >= start,
                ProductInventoryEvent.created_at < end,
            )
        )
        or 0
    )


def _recent_csv_imports(db: Session, merchant: Merchant, start: datetime) -> tuple[int, int]:
    batches = list(
        db.scalars(
            select(ProductImportBatch)
            .where(
                ProductImportBatch.merchant_id == merchant.id,
                ProductImportBatch.created_at >= start,
            )
            .order_by(ProductImportBatch.created_at.desc())
        )
    )
    failed_count = sum(
        1
        for batch in batches
        if batch.status in {"FAILED", "COMPLETED_WITH_ERRORS"} or batch.failed_count > 0
    )
    return len(batches), failed_count


def _pos_task(last_sync_status: str | None, last_synced_at: datetime | None) -> ProDailyBriefTaskRead | None:
    now = datetime.now(timezone.utc)
    comparable_synced_at = None
    if last_synced_at:
        comparable_synced_at = (
            last_synced_at
            if last_synced_at.tzinfo
            else last_synced_at.replace(tzinfo=timezone.utc)
        )
    stale = comparable_synced_at is None or comparable_synced_at < now - timedelta(days=1)
    failed = last_sync_status in {"FAILED", "ERROR", "COMPLETED_WITH_ERRORS"}
    if not stale and not failed:
        return None

    if failed:
        message = "최근 POS 동기화에 오류가 있습니다. 상품 반영 결과를 확인해 주세요."
        priority = "HIGH"
    else:
        message = "최근 24시간 내 POS 동기화 기록이 없습니다. 오늘 재고가 최신인지 확인해 주세요."
        priority = "MEDIUM"

    return ProDailyBriefTaskRead(
        task_type="POS_SYNC_CHECK",
        priority=priority,
        title="POS/CSV 동기화 상태 확인",
        message=message,
        action_label="POS 연동 확인",
        action_href="/merchant/pro/pos",
    )


def build_merchant_pro_daily_brief(db: Session, merchant: Merchant) -> MerchantProDailyBriefRead:
    today_start, today_end = _today_window()
    today = datetime.now(KST).date()

    dashboard = build_merchant_pro_dashboard(db, merchant)
    inventory_alerts = build_merchant_pro_inventory_alerts(db, merchant)
    recommendations = build_merchant_pro_recommendations(db, merchant)
    pos_integration = get_or_create_pos_integration(db, merchant)

    unresolved_alerts = [alert for alert in inventory_alerts.alerts if _is_unresolved(alert)]
    action_started_alert_count = sum(1 for alert in inventory_alerts.alerts if alert.latest_action_type == "ACTION_STARTED")
    high_unresolved_alerts = [
        alert for alert in unresolved_alerts if alert.severity == "HIGH"
    ]

    csv_recent_import_count, csv_recent_failed_count = _recent_csv_imports(db, merchant, today_start)
    inventory_event_count_today = _count_today_inventory_events(db, merchant, today_start, today_end)

    tasks: list[ProDailyBriefTaskRead] = []
    tasks.extend(_alert_task(alert) for alert in sorted(unresolved_alerts, key=lambda item: _priority_key(item.severity))[:3])

    top_recommendations = sorted(
        recommendations.recommendations,
        key=lambda item: (_priority_key(item.action_priority), -item.sell_through_rate),
    )[:3]
    tasks.extend(_recommendation_task(recommendation) for recommendation in top_recommendations)

    pos_status_task = _pos_task(pos_integration.last_sync_status, pos_integration.last_synced_at)
    if pos_status_task:
        tasks.append(pos_status_task)

    if csv_recent_failed_count > 0:
        tasks.append(
            ProDailyBriefTaskRead(
                task_type="CSV_IMPORT_REVIEW",
                priority="MEDIUM",
                title="CSV 업로드 실패 행 확인",
                message=f"오늘 CSV 업로드 중 오류가 있는 배치가 {csv_recent_failed_count}건 있습니다.",
                action_label="CSV 등록 결과 확인",
                action_href="/merchant/products/import",
            )
        )

    if not tasks:
        tasks.append(
            ProDailyBriefTaskRead(
                task_type="RECOMMENDATION_ACTION",
                priority="LOW",
                title="오늘 운영 지표 확인",
                message="큰 운영 이슈는 없습니다. 오늘 판매율과 추천 재고를 가볍게 확인해 주세요.",
                action_label="Pro 대시보드 보기",
                action_href="/merchant/pro",
            )
        )

    tasks = sorted(tasks, key=lambda item: _priority_key(item.priority))[:8]

    return MerchantProDailyBriefRead(
        date=today,
        today_sales_amount=dashboard.today_gross_sales,
        today_reservation_count=dashboard.today_reserved_quantity,
        today_picked_up_count=dashboard.today_picked_up_count,
        today_cancelled_count=dashboard.today_cancelled_count,
        saved_quantity_today=dashboard.today_estimated_saved_items,
        unresolved_alert_count=len(unresolved_alerts),
        action_started_alert_count=action_started_alert_count,
        high_severity_alert_count=len(high_unresolved_alerts),
        recommendation_action_count=len(top_recommendations),
        pos_last_sync_status=pos_integration.last_sync_status,
        pos_last_synced_at=pos_integration.last_synced_at,
        csv_recent_import_count=csv_recent_import_count,
        csv_recent_failed_count=csv_recent_failed_count,
        inventory_event_count_today=inventory_event_count_today,
        tasks=tasks,
    )


def _snapshot_to_read(snapshot: ProDailyBriefSnapshot) -> ProDailyBriefSnapshotRead:
    return ProDailyBriefSnapshotRead.model_validate(snapshot)


def _apply_brief_to_snapshot(snapshot: ProDailyBriefSnapshot, brief: MerchantProDailyBriefRead) -> None:
    snapshot.brief_date = brief.date
    snapshot.today_sales_amount = brief.today_sales_amount
    snapshot.today_reservation_count = brief.today_reservation_count
    snapshot.today_picked_up_count = brief.today_picked_up_count
    snapshot.today_cancelled_count = brief.today_cancelled_count
    snapshot.saved_quantity_today = brief.saved_quantity_today
    snapshot.unresolved_alert_count = brief.unresolved_alert_count
    snapshot.action_started_alert_count = brief.action_started_alert_count
    snapshot.high_severity_alert_count = brief.high_severity_alert_count
    snapshot.recommendation_action_count = brief.recommendation_action_count
    snapshot.pos_last_sync_status = brief.pos_last_sync_status
    snapshot.pos_last_synced_at = brief.pos_last_synced_at
    snapshot.csv_recent_import_count = brief.csv_recent_import_count
    snapshot.csv_recent_failed_count = brief.csv_recent_failed_count
    snapshot.inventory_event_count_today = brief.inventory_event_count_today
    snapshot.updated_at = datetime.now(timezone.utc)


def create_or_update_daily_brief_snapshot(db: Session, merchant: Merchant) -> ProDailyBriefSnapshotRead:
    brief = build_merchant_pro_daily_brief(db, merchant)
    snapshot = db.scalar(
        select(ProDailyBriefSnapshot)
        .where(
            ProDailyBriefSnapshot.merchant_id == merchant.id,
            ProDailyBriefSnapshot.brief_date == brief.date,
        )
        .options(selectinload(ProDailyBriefSnapshot.tasks))
    )
    if snapshot is None:
        snapshot = ProDailyBriefSnapshot(
            merchant_id=merchant.id,
            brief_date=brief.date,
        )
        db.add(snapshot)

    _apply_brief_to_snapshot(snapshot, brief)
    db.flush()

    db.execute(delete(ProDailyBriefTask).where(ProDailyBriefTask.snapshot_id == snapshot.id))
    for task in brief.tasks:
        db.add(
            ProDailyBriefTask(
                snapshot_id=snapshot.id,
                task_type=task.task_type,
                priority=task.priority,
                title=task.title,
                message=task.message,
                action_label=task.action_label,
                action_href=task.action_href,
            )
        )

    db.commit()
    refreshed = db.scalar(
        select(ProDailyBriefSnapshot)
        .where(ProDailyBriefSnapshot.id == snapshot.id)
        .options(selectinload(ProDailyBriefSnapshot.tasks))
    )
    if refreshed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily brief snapshot not found.")
    return _snapshot_to_read(refreshed)


def _history_delta(snapshots: list[ProDailyBriefSnapshot]) -> ProDailyBriefHistoryDeltaRead:
    if len(snapshots) < 2:
        return ProDailyBriefHistoryDeltaRead()

    latest = snapshots[0]
    previous = snapshots[1]
    return ProDailyBriefHistoryDeltaRead(
        unresolved_alert_delta=latest.unresolved_alert_count - previous.unresolved_alert_count,
        sales_delta=latest.today_sales_amount - previous.today_sales_amount,
        reservation_delta=latest.today_reservation_count - previous.today_reservation_count,
        picked_up_delta=latest.today_picked_up_count - previous.today_picked_up_count,
        saved_quantity_delta=latest.saved_quantity_today - previous.saved_quantity_today,
    )


def list_daily_brief_history(
    db: Session,
    merchant: Merchant,
    limit: int = 30,
) -> MerchantProDailyBriefHistoryRead:
    bounded_limit = max(1, min(limit, 30))
    snapshots = list(
        db.scalars(
            select(ProDailyBriefSnapshot)
            .where(ProDailyBriefSnapshot.merchant_id == merchant.id)
            .options(selectinload(ProDailyBriefSnapshot.tasks))
            .order_by(ProDailyBriefSnapshot.brief_date.desc(), ProDailyBriefSnapshot.created_at.desc())
            .limit(bounded_limit)
        )
    )

    latest = snapshots[0] if snapshots else None
    previous = snapshots[1] if len(snapshots) > 1 else None
    return MerchantProDailyBriefHistoryRead(
        snapshots=[_snapshot_to_read(snapshot) for snapshot in snapshots],
        latest_snapshot_id=latest.id if latest else None,
        previous_snapshot_id=previous.id if previous else None,
        delta=_history_delta(snapshots),
    )


def get_daily_brief_snapshot(
    db: Session,
    merchant: Merchant,
    snapshot_id: UUID,
) -> ProDailyBriefSnapshotRead:
    snapshot = db.scalar(
        select(ProDailyBriefSnapshot)
        .where(
            ProDailyBriefSnapshot.id == snapshot_id,
            ProDailyBriefSnapshot.merchant_id == merchant.id,
        )
        .options(selectinload(ProDailyBriefSnapshot.tasks))
    )
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Daily brief snapshot not found.")
    return _snapshot_to_read(snapshot)
