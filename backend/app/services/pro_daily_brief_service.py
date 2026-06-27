import csv
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from io import StringIO
from zoneinfo import ZoneInfo

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.merchant import Merchant
from app.models.pro_daily_brief import ProDailyBriefSnapshot, ProDailyBriefTask
from app.models.pro_weekly_report import (
    ProWeeklyReportBatchRun,
    ProWeeklyReportBatchRunItem,
    ProWeeklyReportDeliveryRun,
    ProWeeklyReportDeliveryRunItem,
    ProWeeklyReportInAppNotification,
    ProWeeklyReportInsight,
    ProWeeklyReportSnapshot,
)
from app.models.product_import import ProductImportBatch
from app.models.product_inventory_event import ProductInventoryEvent
from app.schemas.pro_daily_brief import (
    MerchantProDailyBriefHistoryRead,
    MerchantProDailyBriefRead,
    MerchantProWeeklyReportRead,
    MerchantProWeeklyReportHistoryRead,
    MerchantProWeeklyReportNotificationListRead,
    ProWeeklyReportAutoSnapshotPreviewRead,
    ProWeeklyReportAutoSnapshotRunRead,
    AdminProWeeklyReportBatchRunMonitorRead,
    AdminProWeeklyReportNotificationListRead,
    AdminProWeeklyReportNotificationRead,
    AdminProWeeklyReportNotificationSummaryRead,
    AdminProOperationsAttentionSummaryRead,
    AdminProOperationsBatchSummaryRead,
    AdminProOperationsDeliverySummaryRead,
    AdminProOperationsNotificationSummaryRead,
    AdminProOperationsSummaryRead,
    AdminProWeeklyReportDeliveryRunHistoryRead,
    AdminProWeeklyReportBatchRunSummaryRead,
    AdminWeeklyReportBatchPreviewRead,
    MerchantProWeeklyReportBatchRunHistoryRead,
    MerchantProWeeklyReportReadAllResultRead,
    MerchantProWeeklyReportUnreadCountRead,
    ProDailyBriefHistoryDeltaRead,
    ProDailyBriefSnapshotRead,
    ProDailyBriefTaskRead,
    ProWeeklyReportBatchRunRead,
    ProWeeklyReportDeliveryRunRead,
    ProWeeklyReportInAppNotificationRead,
    ProWeeklyReportSnapshotRead,
    ProWeeklyReportDailyTrendRead,
    ProWeeklyReportInsightRead,
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
MAX_WEEKLY_REPORT_DAYS = 31
ZERO = Decimal("0.00")


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


def _default_report_range() -> tuple[date, date]:
    end_date = datetime.now(KST).date()
    return end_date - timedelta(days=6), end_date


def _date_span(start_date: date, end_date: date) -> list[date]:
    if end_date < start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="end_date must be after start_date.")
    if (end_date - start_date).days + 1 > MAX_WEEKLY_REPORT_DAYS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Weekly report range cannot exceed 31 days.")
    return [start_date + timedelta(days=offset) for offset in range((end_date - start_date).days + 1)]


def _trend_from_snapshot(snapshot: ProDailyBriefSnapshot) -> ProWeeklyReportDailyTrendRead:
    return ProWeeklyReportDailyTrendRead(
        date=snapshot.brief_date,
        sales_amount=snapshot.today_sales_amount,
        reservation_count=snapshot.today_reservation_count,
        picked_up_count=snapshot.today_picked_up_count,
        cancelled_count=snapshot.today_cancelled_count,
        saved_quantity=snapshot.saved_quantity_today,
        unresolved_alert_count=snapshot.unresolved_alert_count,
        recommendation_action_count=snapshot.recommendation_action_count,
    )


def _trend_from_brief(brief: MerchantProDailyBriefRead) -> ProWeeklyReportDailyTrendRead:
    return ProWeeklyReportDailyTrendRead(
        date=brief.date,
        sales_amount=brief.today_sales_amount,
        reservation_count=brief.today_reservation_count,
        picked_up_count=brief.today_picked_up_count,
        cancelled_count=brief.today_cancelled_count,
        saved_quantity=brief.saved_quantity_today,
        unresolved_alert_count=brief.unresolved_alert_count,
        recommendation_action_count=brief.recommendation_action_count,
    )


def _empty_trend(target_date: date) -> ProWeeklyReportDailyTrendRead:
    return ProWeeklyReportDailyTrendRead(
        date=target_date,
        sales_amount=0,
        reservation_count=0,
        picked_up_count=0,
        cancelled_count=0,
        saved_quantity=0,
        unresolved_alert_count=0,
        recommendation_action_count=0,
    )


def _build_weekly_insights(
    trends: list[ProWeeklyReportDailyTrendRead],
    snapshot_days_count: int,
    total_recommendation_action_count: int,
    pos_sync_issue_count: int,
    csv_import_error_count: int,
) -> list[ProWeeklyReportInsightRead]:
    insights: list[ProWeeklyReportInsightRead] = []

    first_with_data = next((trend for trend in trends if trend.sales_amount or trend.reservation_count or trend.unresolved_alert_count), None)
    last_with_data = next(
        (trend for trend in reversed(trends) if trend.sales_amount or trend.reservation_count or trend.unresolved_alert_count),
        None,
    )
    if first_with_data and last_with_data and first_with_data.date != last_with_data.date:
        alert_delta = last_with_data.unresolved_alert_count - first_with_data.unresolved_alert_count
        if alert_delta < 0:
            insights.append(
                ProWeeklyReportInsightRead(
                    title="미해결 알림이 줄었습니다",
                    message=f"기간 시작 대비 미해결 알림이 {abs(alert_delta)}건 줄었습니다.",
                    severity="POSITIVE",
                )
            )
        elif alert_delta > 0:
            insights.append(
                ProWeeklyReportInsightRead(
                    title="미해결 알림 확인이 필요합니다",
                    message=f"기간 시작 대비 미해결 알림이 {alert_delta}건 늘었습니다.",
                    severity="WARNING",
                )
            )

        saved_delta = last_with_data.saved_quantity - first_with_data.saved_quantity
        if saved_delta > 0:
            insights.append(
                ProWeeklyReportInsightRead(
                    title="폐기 절감 수량이 증가했습니다",
                    message=f"기간 시작 대비 일간 폐기 절감 수량이 {saved_delta}개 늘었습니다.",
                    severity="POSITIVE",
                )
            )

    total_reservations = sum(trend.reservation_count for trend in trends)
    total_picked_up = sum(trend.picked_up_count for trend in trends)
    if total_reservations > 0:
        pickup_rate = total_picked_up / total_reservations * 100
        if pickup_rate < 60:
            insights.append(
                ProWeeklyReportInsightRead(
                    title="픽업 완료율을 확인해야 합니다",
                    message=f"최근 기간 픽업 완료율이 {pickup_rate:.1f}%입니다. 픽업 시간과 고객 안내를 점검해 주세요.",
                    severity="WARNING",
                )
            )

    if total_recommendation_action_count < 3:
        insights.append(
            ProWeeklyReportInsightRead(
                title="추천 액션 실행이 적습니다",
                message="추천 액션이 적게 기록되었습니다. 추천 화면에서 재고/할인가 제안을 확인해 보세요.",
                severity="INFO",
            )
        )

    if pos_sync_issue_count > 0:
        insights.append(
            ProWeeklyReportInsightRead(
                title="POS 동기화 상태 점검",
                message=f"POS 동기화 확인이 필요한 날짜가 {pos_sync_issue_count}일 있습니다.",
                severity="WARNING",
            )
        )

    if csv_import_error_count > 0:
        insights.append(
            ProWeeklyReportInsightRead(
                title="CSV 업로드 오류 확인",
                message=f"CSV import 오류가 총 {csv_import_error_count}건 기록되었습니다.",
                severity="WARNING",
            )
        )

    if snapshot_days_count < len(trends):
        insights.append(
            ProWeeklyReportInsightRead(
                title="전일 브리프가 쌓일수록 더 정확해집니다",
                message="저장된 Daily Brief가 없는 날짜는 0으로 표시됩니다. 매일 브리프를 저장하면 추이가 더 선명해집니다.",
                severity="INFO",
            )
        )

    if not insights:
        insights.append(
            ProWeeklyReportInsightRead(
                title="이번 주 운영 흐름이 안정적입니다",
                message="큰 경고 신호는 없습니다. Daily Brief를 계속 저장해 운영 개선 흐름을 추적하세요.",
                severity="POSITIVE",
            )
        )

    return insights[:6]


def build_merchant_pro_weekly_report(
    db: Session,
    merchant: Merchant,
    start_date: date | None = None,
    end_date: date | None = None,
) -> MerchantProWeeklyReportRead:
    if start_date is None or end_date is None:
        default_start, default_end = _default_report_range()
        start_date = start_date or default_start
        end_date = end_date or default_end

    dates = _date_span(start_date, end_date)
    today = datetime.now(KST).date()

    snapshots = list(
        db.scalars(
            select(ProDailyBriefSnapshot)
            .where(
                ProDailyBriefSnapshot.merchant_id == merchant.id,
                ProDailyBriefSnapshot.brief_date >= start_date,
                ProDailyBriefSnapshot.brief_date <= end_date,
            )
            .order_by(ProDailyBriefSnapshot.brief_date.asc())
        )
    )
    snapshots_by_date = {snapshot.brief_date: snapshot for snapshot in snapshots}

    live_today = None
    if start_date <= today <= end_date and today not in snapshots_by_date:
        live_today = build_merchant_pro_daily_brief(db, merchant)

    daily_trends: list[ProWeeklyReportDailyTrendRead] = []
    pos_sync_issue_count = 0
    csv_import_error_count = 0
    high_severity_alert_count = 0
    total_inventory_event_count = 0
    snapshot_days_count = len(snapshots)

    for target_date in dates:
        snapshot = snapshots_by_date.get(target_date)
        if snapshot:
            trend = _trend_from_snapshot(snapshot)
            if snapshot.pos_last_sync_status != "COMPLETED":
                pos_sync_issue_count += 1
            csv_import_error_count += snapshot.csv_recent_failed_count
            high_severity_alert_count += snapshot.high_severity_alert_count
            total_inventory_event_count += snapshot.inventory_event_count_today
        elif live_today and target_date == live_today.date:
            trend = _trend_from_brief(live_today)
            if live_today.pos_last_sync_status != "COMPLETED":
                pos_sync_issue_count += 1
            csv_import_error_count += live_today.csv_recent_failed_count
            high_severity_alert_count += live_today.high_severity_alert_count
            total_inventory_event_count += live_today.inventory_event_count_today
        else:
            trend = _empty_trend(target_date)
        daily_trends.append(trend)

    total_sales_amount = sum((trend.sales_amount for trend in daily_trends), start=ZERO)
    total_reservation_count = sum(trend.reservation_count for trend in daily_trends)
    total_picked_up_count = sum(trend.picked_up_count for trend in daily_trends)
    total_cancelled_count = sum(trend.cancelled_count for trend in daily_trends)
    total_saved_quantity = sum(trend.saved_quantity for trend in daily_trends)
    total_recommendation_action_count = sum(trend.recommendation_action_count for trend in daily_trends)
    average_unresolved_alert_count = (
        sum(trend.unresolved_alert_count for trend in daily_trends) / len(daily_trends)
        if daily_trends
        else 0.0
    )

    return MerchantProWeeklyReportRead(
        start_date=start_date,
        end_date=end_date,
        total_sales_amount=total_sales_amount,
        total_reservation_count=total_reservation_count,
        total_picked_up_count=total_picked_up_count,
        total_cancelled_count=total_cancelled_count,
        total_saved_quantity=total_saved_quantity,
        average_unresolved_alert_count=round(average_unresolved_alert_count, 1),
        high_severity_alert_count=high_severity_alert_count,
        total_recommendation_action_count=total_recommendation_action_count,
        total_inventory_event_count=total_inventory_event_count,
        pos_sync_issue_count=pos_sync_issue_count,
        csv_import_error_count=csv_import_error_count,
        snapshot_days_count=snapshot_days_count + (1 if live_today else 0),
        daily_trends=daily_trends,
        insights=_build_weekly_insights(
            daily_trends,
            snapshot_days_count + (1 if live_today else 0),
            total_recommendation_action_count,
            pos_sync_issue_count,
            csv_import_error_count,
        ),
    )


def weekly_report_to_csv(report: MerchantProWeeklyReportRead) -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "date",
            "sales_amount",
            "reservation_count",
            "picked_up_count",
            "cancelled_count",
            "saved_quantity",
            "unresolved_alert_count",
            "recommendation_action_count",
        ]
    )
    for trend in report.daily_trends:
        writer.writerow(
            [
                trend.date.isoformat(),
                trend.sales_amount,
                trend.reservation_count,
                trend.picked_up_count,
                trend.cancelled_count,
                trend.saved_quantity,
                trend.unresolved_alert_count,
                trend.recommendation_action_count,
            ]
        )
    return output.getvalue()


def weekly_report_to_text(report: MerchantProWeeklyReportRead) -> str:
    insight_lines = "\n".join(
        f"- {insight.title}: {insight.message}" for insight in report.insights
    )
    if not insight_lines:
        insight_lines = "- 표시할 인사이트가 없습니다."

    return "\n".join(
        [
            "BreadGo Pro 주간 운영 리포트",
            f"기간: {report.start_date.isoformat()} ~ {report.end_date.isoformat()}",
            "",
            "[이번 주 운영 요약]",
            f"- 총 매출: {int(report.total_sales_amount):,}원",
            f"- 예약 수: {report.total_reservation_count}건",
            f"- 픽업 완료: {report.total_picked_up_count}건",
            f"- 취소: {report.total_cancelled_count}건",
            f"- 폐기 절감: {report.total_saved_quantity}개",
            f"- 평균 미해결 알림: {report.average_unresolved_alert_count:.1f}건",
            f"- HIGH 알림: {report.high_severity_alert_count}건",
            f"- 추천 액션: {report.total_recommendation_action_count}건",
            f"- 재고 변경 이력: {report.total_inventory_event_count}건",
            f"- POS 확인 필요 일수: {report.pos_sync_issue_count}일",
            f"- CSV 오류: {report.csv_import_error_count}건",
            "",
            "[주요 인사이트]",
            insight_lines,
            "",
            "이 요약은 실제 AI 생성 문장이 아닌 BreadGo Pro rule-based 운영 리포트입니다.",
        ]
    )


def _weekly_snapshot_to_read(snapshot: ProWeeklyReportSnapshot) -> ProWeeklyReportSnapshotRead:
    return ProWeeklyReportSnapshotRead.model_validate(snapshot)


def _apply_weekly_report_to_snapshot(
    snapshot: ProWeeklyReportSnapshot,
    report: MerchantProWeeklyReportRead,
) -> None:
    snapshot.start_date = report.start_date
    snapshot.end_date = report.end_date
    snapshot.total_sales_amount = report.total_sales_amount
    snapshot.total_reservation_count = report.total_reservation_count
    snapshot.total_picked_up_count = report.total_picked_up_count
    snapshot.total_cancelled_count = report.total_cancelled_count
    snapshot.total_saved_quantity = report.total_saved_quantity
    snapshot.average_unresolved_alert_count = Decimal(str(report.average_unresolved_alert_count))
    snapshot.high_severity_alert_count = report.high_severity_alert_count
    snapshot.total_recommendation_action_count = report.total_recommendation_action_count
    snapshot.total_inventory_event_count = report.total_inventory_event_count
    snapshot.pos_sync_issue_count = report.pos_sync_issue_count
    snapshot.csv_import_error_count = report.csv_import_error_count
    snapshot.text_summary = weekly_report_to_text(report)
    snapshot.updated_at = datetime.now(timezone.utc)


def _find_weekly_report_snapshot(
    db: Session,
    merchant: Merchant,
    start_date: date,
    end_date: date,
) -> ProWeeklyReportSnapshot | None:
    return db.scalar(
        select(ProWeeklyReportSnapshot)
        .where(
            ProWeeklyReportSnapshot.merchant_id == merchant.id,
            ProWeeklyReportSnapshot.start_date == start_date,
            ProWeeklyReportSnapshot.end_date == end_date,
        )
        .options(selectinload(ProWeeklyReportSnapshot.insights))
    )


def _create_or_update_weekly_report_snapshot_with_status(
    db: Session,
    merchant: Merchant,
    start_date: date | None = None,
    end_date: date | None = None,
) -> tuple[ProWeeklyReportSnapshotRead, str]:
    report = build_merchant_pro_weekly_report(db, merchant, start_date=start_date, end_date=end_date)
    snapshot = _find_weekly_report_snapshot(db, merchant, report.start_date, report.end_date)
    created_or_updated = "UPDATED"
    if snapshot is None:
        snapshot = ProWeeklyReportSnapshot(
            merchant_id=merchant.id,
            start_date=report.start_date,
            end_date=report.end_date,
        )
        db.add(snapshot)
        created_or_updated = "CREATED"

    _apply_weekly_report_to_snapshot(snapshot, report)
    db.flush()

    db.execute(delete(ProWeeklyReportInsight).where(ProWeeklyReportInsight.snapshot_id == snapshot.id))
    for insight in report.insights:
        db.add(
            ProWeeklyReportInsight(
                snapshot_id=snapshot.id,
                title=insight.title,
                message=insight.message,
                severity=insight.severity,
            )
        )

    db.commit()
    refreshed = db.scalar(
        select(ProWeeklyReportSnapshot)
        .where(ProWeeklyReportSnapshot.id == snapshot.id)
        .options(selectinload(ProWeeklyReportSnapshot.insights))
    )
    if refreshed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report snapshot not found.")
    return _weekly_snapshot_to_read(refreshed), created_or_updated


def create_or_update_weekly_report_snapshot(
    db: Session,
    merchant: Merchant,
    start_date: date | None = None,
    end_date: date | None = None,
) -> ProWeeklyReportSnapshotRead:
    snapshot, _created_or_updated = _create_or_update_weekly_report_snapshot_with_status(
        db,
        merchant,
        start_date=start_date,
        end_date=end_date,
    )
    return snapshot


def preview_auto_weekly_snapshot(
    db: Session,
    merchant: Merchant,
    start_date: date | None = None,
    end_date: date | None = None,
) -> ProWeeklyReportAutoSnapshotPreviewRead:
    report = build_merchant_pro_weekly_report(db, merchant, start_date=start_date, end_date=end_date)
    existing_snapshot = _find_weekly_report_snapshot(db, merchant, report.start_date, report.end_date)
    return ProWeeklyReportAutoSnapshotPreviewRead(
        start_date=report.start_date,
        end_date=report.end_date,
        would_create_new=existing_snapshot is None,
        existing_snapshot_id=existing_snapshot.id if existing_snapshot else None,
        report_summary=report,
        insights=report.insights,
    )


def create_current_week_snapshot(
    db: Session,
    merchant: Merchant,
    start_date: date | None = None,
    end_date: date | None = None,
) -> ProWeeklyReportAutoSnapshotRunRead:
    snapshot, created_or_updated = _create_or_update_weekly_report_snapshot_with_status(
        db,
        merchant,
        start_date=start_date,
        end_date=end_date,
    )
    message = (
        "자동 저장 준비 흐름으로 새 주간 리포트 snapshot을 생성했습니다."
        if created_or_updated == "CREATED"
        else "자동 저장 준비 흐름으로 기존 주간 리포트 snapshot을 최신 값으로 업데이트했습니다."
    )
    return ProWeeklyReportAutoSnapshotRunRead(
        snapshot_id=snapshot.id,
        created_or_updated=created_or_updated,
        start_date=snapshot.start_date,
        end_date=snapshot.end_date,
        message=message,
    )


def _batch_run_to_read(batch_run: ProWeeklyReportBatchRun) -> ProWeeklyReportBatchRunRead:
    return ProWeeklyReportBatchRunRead.model_validate(batch_run)


def create_weekly_report_batch_test_run(
    db: Session,
    merchant: Merchant,
    start_date: date | None = None,
    end_date: date | None = None,
) -> ProWeeklyReportBatchRunRead:
    report = build_merchant_pro_weekly_report(db, merchant, start_date=start_date, end_date=end_date)
    now = datetime.now(timezone.utc)
    batch_run = ProWeeklyReportBatchRun(
        run_type="MANUAL_TEST",
        status="STARTED",
        start_date=report.start_date,
        end_date=report.end_date,
        target_merchant_count=1,
        success_count=0,
        failed_count=0,
        skipped_count=0,
        message="Weekly Report 자동 생성 테스트를 시작했습니다.",
        created_at=now,
    )
    db.add(batch_run)
    db.flush()

    try:
        snapshot_result = create_current_week_snapshot(
            db,
            merchant,
            start_date=report.start_date,
            end_date=report.end_date,
        )
        item = ProWeeklyReportBatchRunItem(
            batch_run_id=batch_run.id,
            merchant_id=merchant.id,
            snapshot_id=snapshot_result.snapshot_id,
            status="SUCCESS",
            message=snapshot_result.message,
        )
        batch_run.status = "COMPLETED"
        batch_run.success_count = 1
        batch_run.message = "Weekly Report 자동 생성 테스트가 완료되었습니다."
    except Exception as exc:
        item = ProWeeklyReportBatchRunItem(
            batch_run_id=batch_run.id,
            merchant_id=merchant.id,
            status="FAILED",
            message=str(exc),
        )
        batch_run.status = "FAILED"
        batch_run.failed_count = 1
        batch_run.message = "Weekly Report 자동 생성 테스트가 실패했습니다."

    batch_run.completed_at = datetime.now(timezone.utc)
    db.add(item)
    db.commit()
    refreshed = db.scalar(
        select(ProWeeklyReportBatchRun)
        .where(ProWeeklyReportBatchRun.id == batch_run.id)
        .options(selectinload(ProWeeklyReportBatchRun.items))
    )
    if refreshed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report batch run not found.")
    return _batch_run_to_read(refreshed)


def list_weekly_report_batch_runs(
    db: Session,
    merchant: Merchant,
    limit: int = 20,
) -> MerchantProWeeklyReportBatchRunHistoryRead:
    bounded_limit = max(1, min(limit, 50))
    batch_runs = list(
        db.scalars(
            select(ProWeeklyReportBatchRun)
            .join(ProWeeklyReportBatchRunItem)
            .where(ProWeeklyReportBatchRunItem.merchant_id == merchant.id)
            .options(selectinload(ProWeeklyReportBatchRun.items))
            .order_by(ProWeeklyReportBatchRun.created_at.desc())
            .limit(bounded_limit)
        )
        .unique()
    )
    return MerchantProWeeklyReportBatchRunHistoryRead(batch_runs=[_batch_run_to_read(run) for run in batch_runs])


def get_weekly_report_batch_run(
    db: Session,
    merchant: Merchant,
    batch_run_id: UUID,
) -> ProWeeklyReportBatchRunRead:
    batch_run = db.scalar(
        select(ProWeeklyReportBatchRun)
        .join(ProWeeklyReportBatchRunItem)
        .where(
            ProWeeklyReportBatchRun.id == batch_run_id,
            ProWeeklyReportBatchRunItem.merchant_id == merchant.id,
        )
        .options(selectinload(ProWeeklyReportBatchRun.items))
    )
    if batch_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report batch run not found.")
    return _batch_run_to_read(batch_run)


def list_admin_weekly_report_batch_runs(
    db: Session,
    status_filter: str | None = None,
    run_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 50,
) -> AdminProWeeklyReportBatchRunMonitorRead:
    conditions = []
    if status_filter:
        conditions.append(ProWeeklyReportBatchRun.status == status_filter)
    if run_type:
        conditions.append(ProWeeklyReportBatchRun.run_type == run_type)
    if start_date:
        conditions.append(ProWeeklyReportBatchRun.start_date >= start_date)
    if end_date:
        conditions.append(ProWeeklyReportBatchRun.end_date <= end_date)

    base_query = select(ProWeeklyReportBatchRun).where(*conditions)
    all_runs = list(db.scalars(base_query.order_by(ProWeeklyReportBatchRun.created_at.desc())))
    bounded_limit = max(1, min(limit, 100))
    runs = list(
        db.scalars(
            base_query.options(selectinload(ProWeeklyReportBatchRun.items))
            .order_by(ProWeeklyReportBatchRun.created_at.desc())
            .limit(bounded_limit)
        )
    )
    latest = all_runs[0] if all_runs else None
    summary = AdminProWeeklyReportBatchRunSummaryRead(
        total_runs=len(all_runs),
        completed_count=sum(1 for run in all_runs if run.status == "COMPLETED"),
        failed_count=sum(1 for run in all_runs if run.status == "FAILED"),
        partial_count=sum(1 for run in all_runs if run.status == "PARTIAL"),
        latest_run_status=latest.status if latest else None,
        latest_run_at=latest.created_at if latest else None,
    )
    return AdminProWeeklyReportBatchRunMonitorRead(
        summary=summary,
        batch_runs=[_batch_run_to_read(run) for run in runs],
    )


def get_admin_weekly_report_batch_run(
    db: Session,
    batch_run_id: UUID,
) -> ProWeeklyReportBatchRunRead:
    batch_run = db.scalar(
        select(ProWeeklyReportBatchRun)
        .where(ProWeeklyReportBatchRun.id == batch_run_id)
        .options(selectinload(ProWeeklyReportBatchRun.items))
    )
    if batch_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report batch run not found.")
    return _batch_run_to_read(batch_run)


def retry_failed_weekly_report_batch_items(
    db: Session,
    batch_run_id: UUID,
) -> ProWeeklyReportBatchRunRead:
    original = db.scalar(
        select(ProWeeklyReportBatchRun)
        .where(ProWeeklyReportBatchRun.id == batch_run_id)
        .options(selectinload(ProWeeklyReportBatchRun.items))
    )
    if original is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report batch run not found.")

    failed_items = [item for item in original.items if item.status == "FAILED"]
    if not failed_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="재실행할 실패 item이 없습니다.")

    failed_merchant_ids = [item.merchant_id for item in failed_items]
    merchants = list(
        db.scalars(
            select(Merchant)
            .where(Merchant.id.in_(failed_merchant_ids))
            .order_by(Merchant.created_at.asc())
        )
    )
    merchant_by_id = {merchant.id: merchant for merchant in merchants}
    batch_run = ProWeeklyReportBatchRun(
        run_type="RETRY",
        status="STARTED",
        start_date=original.start_date,
        end_date=original.end_date,
        target_merchant_count=len(failed_items),
        success_count=0,
        failed_count=0,
        skipped_count=0,
        message=f"원본 batch run {batch_run_id}의 실패 item을 재실행합니다.",
        created_at=datetime.now(timezone.utc),
    )
    db.add(batch_run)
    db.flush()

    success_count = 0
    failed_count = 0
    skipped_count = 0

    for item in failed_items:
        merchant = merchant_by_id.get(item.merchant_id)
        if merchant is None:
            db.add(
                ProWeeklyReportBatchRunItem(
                    batch_run_id=batch_run.id,
                    merchant_id=item.merchant_id,
                    status="FAILED",
                    message="대상 가맹점을 찾을 수 없어 재실행하지 못했습니다.",
                )
            )
            failed_count += 1
            continue

        try:
            snapshot_result = create_current_week_snapshot(
                db,
                merchant,
                start_date=original.start_date,
                end_date=original.end_date,
            )
            db.add(
                ProWeeklyReportBatchRunItem(
                    batch_run_id=batch_run.id,
                    merchant_id=merchant.id,
                    snapshot_id=snapshot_result.snapshot_id,
                    status="SUCCESS",
                    message=snapshot_result.message,
                )
            )
            success_count += 1
        except Exception as exc:
            db.add(
                ProWeeklyReportBatchRunItem(
                    batch_run_id=batch_run.id,
                    merchant_id=merchant.id,
                    status="FAILED",
                    message=str(exc),
                )
            )
            failed_count += 1

    if failed_count and success_count:
        batch_run.status = "PARTIAL"
        batch_run.message = f"원본 batch run {batch_run_id}의 실패 item 일부 재실행이 실패했습니다."
    elif failed_count and not success_count:
        batch_run.status = "FAILED"
        batch_run.message = f"원본 batch run {batch_run_id}의 실패 item 재실행이 모두 실패했습니다."
    else:
        batch_run.status = "COMPLETED"
        batch_run.message = f"원본 batch run {batch_run_id}의 실패 item 재실행이 완료되었습니다."

    batch_run.success_count = success_count
    batch_run.failed_count = failed_count
    batch_run.skipped_count = skipped_count
    batch_run.completed_at = datetime.now(timezone.utc)
    db.commit()

    refreshed = db.scalar(
        select(ProWeeklyReportBatchRun)
        .where(ProWeeklyReportBatchRun.id == batch_run.id)
        .options(selectinload(ProWeeklyReportBatchRun.items))
    )
    if refreshed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report batch run not found.")
    return _batch_run_to_read(refreshed)


def _delivery_run_to_read(delivery_run: ProWeeklyReportDeliveryRun) -> ProWeeklyReportDeliveryRunRead:
    return ProWeeklyReportDeliveryRunRead.model_validate(delivery_run)


def create_weekly_report_delivery_preview(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
) -> ProWeeklyReportDeliveryRunRead:
    default_start, default_end = _default_report_range()
    resolved_start = start_date or default_start
    resolved_end = end_date or default_end
    merchants = list(db.scalars(select(Merchant).order_by(Merchant.created_at.asc())))
    delivery_run = ProWeeklyReportDeliveryRun(
        run_type="PREVIEW",
        channel="IN_APP_PREVIEW",
        status="PENDING",
        period_start=resolved_start,
        period_end=resolved_end,
        total_count=len(merchants),
        ready_count=0,
        skipped_count=0,
        failed_count=0,
        message="Weekly Report 외부 발송 전 preview를 생성했습니다. 실제 발송은 하지 않습니다.",
        created_at=datetime.now(timezone.utc),
    )
    db.add(delivery_run)
    db.flush()

    ready_count = 0
    skipped_count = 0
    failed_count = 0

    for merchant in merchants:
        try:
            snapshot = db.scalar(
                select(ProWeeklyReportSnapshot)
                .where(
                    ProWeeklyReportSnapshot.merchant_id == merchant.id,
                    ProWeeklyReportSnapshot.start_date == resolved_start,
                    ProWeeklyReportSnapshot.end_date == resolved_end,
                )
                .order_by(ProWeeklyReportSnapshot.updated_at.desc())
            )
            if snapshot is None:
                db.add(
                    ProWeeklyReportDeliveryRunItem(
                        delivery_run_id=delivery_run.id,
                        merchant_id=merchant.id,
                        status="SKIPPED",
                        reason="해당 기간의 Weekly Report snapshot이 없어 발송 준비 대상에서 제외했습니다.",
                    )
                )
                skipped_count += 1
                continue

            db.add(
                ProWeeklyReportDeliveryRunItem(
                    delivery_run_id=delivery_run.id,
                    merchant_id=merchant.id,
                    snapshot_id=snapshot.id,
                    status="READY",
                    reason="해당 기간 Weekly Report snapshot이 있어 발송 준비가 가능합니다.",
                )
            )
            ready_count += 1
        except Exception as exc:
            db.add(
                ProWeeklyReportDeliveryRunItem(
                    delivery_run_id=delivery_run.id,
                    merchant_id=merchant.id,
                    status="FAILED",
                    reason=str(exc),
                )
            )
            failed_count += 1

    delivery_run.ready_count = ready_count
    delivery_run.skipped_count = skipped_count
    delivery_run.failed_count = failed_count
    if failed_count and ready_count:
        delivery_run.status = "PARTIAL"
        delivery_run.message = "일부 merchant의 Weekly Report delivery preview 생성이 실패했습니다."
    elif failed_count and not ready_count:
        delivery_run.status = "FAILED"
        delivery_run.message = "Weekly Report delivery preview가 실패했습니다."
    else:
        delivery_run.status = "COMPLETED"
    delivery_run.completed_at = datetime.now(timezone.utc)
    db.commit()

    refreshed = db.scalar(
        select(ProWeeklyReportDeliveryRun)
        .where(ProWeeklyReportDeliveryRun.id == delivery_run.id)
        .options(selectinload(ProWeeklyReportDeliveryRun.items))
    )
    if refreshed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report delivery run not found.")
    return _delivery_run_to_read(refreshed)


def list_weekly_report_delivery_runs(
    db: Session,
    limit: int = 50,
) -> AdminProWeeklyReportDeliveryRunHistoryRead:
    bounded_limit = max(1, min(limit, 100))
    delivery_runs = list(
        db.scalars(
            select(ProWeeklyReportDeliveryRun)
            .options(selectinload(ProWeeklyReportDeliveryRun.items))
            .order_by(ProWeeklyReportDeliveryRun.created_at.desc())
            .limit(bounded_limit)
        )
    )
    return AdminProWeeklyReportDeliveryRunHistoryRead(
        delivery_runs=[_delivery_run_to_read(run) for run in delivery_runs]
    )


def get_weekly_report_delivery_run(
    db: Session,
    delivery_run_id: UUID,
) -> ProWeeklyReportDeliveryRunRead:
    delivery_run = db.scalar(
        select(ProWeeklyReportDeliveryRun)
        .where(ProWeeklyReportDeliveryRun.id == delivery_run_id)
        .options(selectinload(ProWeeklyReportDeliveryRun.items))
    )
    if delivery_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report delivery run not found.")
    return _delivery_run_to_read(delivery_run)


def create_weekly_report_in_app_mock_delivery(
    db: Session,
    delivery_run_id: UUID,
) -> ProWeeklyReportDeliveryRunRead:
    source_run = db.scalar(
        select(ProWeeklyReportDeliveryRun)
        .where(ProWeeklyReportDeliveryRun.id == delivery_run_id)
        .options(selectinload(ProWeeklyReportDeliveryRun.items))
    )
    if source_run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report delivery run not found.")

    ready_items = [item for item in source_run.items if item.status == "READY"]
    if not ready_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="mock delivery 대상 READY item이 없습니다.")

    mock_run = ProWeeklyReportDeliveryRun(
        run_type="IN_APP_MOCK",
        channel="IN_APP",
        status="PENDING",
        period_start=source_run.period_start,
        period_end=source_run.period_end,
        total_count=len(ready_items),
        ready_count=0,
        skipped_count=0,
        failed_count=0,
        message=f"delivery run {delivery_run_id}의 READY item을 BreadGo 내부 알림으로 mock delivery 처리합니다.",
        created_at=datetime.now(timezone.utc),
    )
    db.add(mock_run)
    db.flush()

    sent_count = 0
    skipped_count = 0
    failed_count = 0

    for source_item in ready_items:
        try:
            if source_item.snapshot_id is None:
                db.add(
                    ProWeeklyReportDeliveryRunItem(
                        delivery_run_id=mock_run.id,
                        merchant_id=source_item.merchant_id,
                        status="SKIPPED",
                        reason="snapshot_id가 없어 내부 알림 mock delivery 대상에서 제외했습니다.",
                    )
                )
                skipped_count += 1
                continue

            result_item = ProWeeklyReportDeliveryRunItem(
                delivery_run_id=mock_run.id,
                merchant_id=source_item.merchant_id,
                snapshot_id=source_item.snapshot_id,
                status="SENT",
                reason="Weekly Report 내부 알림 mock delivery를 생성했습니다.",
            )
            db.add(result_item)
            db.flush()
            db.add(
                ProWeeklyReportInAppNotification(
                    merchant_id=source_item.merchant_id,
                    snapshot_id=source_item.snapshot_id,
                    delivery_run_id=mock_run.id,
                    delivery_run_item_id=result_item.id,
                    title="Weekly Report가 준비되었습니다",
                    message="이번 주 Weekly Report가 준비되었습니다. BreadGo Pro에서 최근 7일 리포트를 확인할 수 있습니다.",
                    status="UNREAD",
                    created_at=datetime.now(timezone.utc),
                )
            )
            sent_count += 1
        except Exception as exc:
            db.add(
                ProWeeklyReportDeliveryRunItem(
                    delivery_run_id=mock_run.id,
                    merchant_id=source_item.merchant_id,
                    snapshot_id=source_item.snapshot_id,
                    status="FAILED",
                    reason=str(exc),
                )
            )
            failed_count += 1

    mock_run.ready_count = sent_count
    mock_run.skipped_count = skipped_count
    mock_run.failed_count = failed_count
    if failed_count and sent_count:
        mock_run.status = "PARTIAL"
        mock_run.message = "일부 Weekly Report 내부 알림 mock delivery가 실패했습니다."
    elif failed_count and not sent_count:
        mock_run.status = "FAILED"
        mock_run.message = "Weekly Report 내부 알림 mock delivery가 실패했습니다."
    else:
        mock_run.status = "COMPLETED"
        mock_run.message = "Weekly Report 내부 알림 mock delivery가 완료되었습니다. 실제 외부 발송은 하지 않았습니다."
    mock_run.completed_at = datetime.now(timezone.utc)
    db.commit()

    refreshed = db.scalar(
        select(ProWeeklyReportDeliveryRun)
        .where(ProWeeklyReportDeliveryRun.id == mock_run.id)
        .options(selectinload(ProWeeklyReportDeliveryRun.items))
    )
    if refreshed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report delivery run not found.")
    return _delivery_run_to_read(refreshed)


def create_weekly_report_unread_reminders(db: Session) -> ProWeeklyReportDeliveryRunRead:
    targets = list(
        db.scalars(
            select(ProWeeklyReportInAppNotification)
            .where(
                ProWeeklyReportInAppNotification.status == "UNREAD",
                ProWeeklyReportInAppNotification.snapshot_id.is_not(None),
                ~ProWeeklyReportInAppNotification.title.contains("리마인드"),
                ~ProWeeklyReportInAppNotification.message.contains("리마인드"),
            )
            .order_by(ProWeeklyReportInAppNotification.created_at.asc())
        )
    )
    if not targets:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="리마인드 대상 미확인 알림이 없습니다.")

    first_target = targets[0]
    snapshot = db.scalar(
        select(ProWeeklyReportSnapshot).where(ProWeeklyReportSnapshot.id == first_target.snapshot_id)
    )
    period_start = snapshot.start_date if snapshot else datetime.now(KST).date()
    period_end = snapshot.end_date if snapshot else datetime.now(KST).date()

    reminder_run = ProWeeklyReportDeliveryRun(
        run_type="IN_APP_REMINDER",
        channel="IN_APP",
        status="PENDING",
        period_start=period_start,
        period_end=period_end,
        total_count=len(targets),
        ready_count=0,
        skipped_count=0,
        failed_count=0,
        message="미확인 Weekly Report 내부 알림을 대상으로 리마인드 mock delivery를 실행합니다.",
        created_at=datetime.now(timezone.utc),
    )
    db.add(reminder_run)
    db.flush()

    sent_count = 0
    skipped_count = 0
    failed_count = 0

    for target in targets:
        try:
            existing_reminder = db.scalar(
                select(ProWeeklyReportInAppNotification)
                .where(
                    ProWeeklyReportInAppNotification.merchant_id == target.merchant_id,
                    ProWeeklyReportInAppNotification.snapshot_id == target.snapshot_id,
                    ProWeeklyReportInAppNotification.status == "UNREAD",
                    ProWeeklyReportInAppNotification.title.contains("리마인드"),
                )
                .order_by(ProWeeklyReportInAppNotification.created_at.desc())
            )
            if existing_reminder is not None:
                db.add(
                    ProWeeklyReportDeliveryRunItem(
                        delivery_run_id=reminder_run.id,
                        merchant_id=target.merchant_id,
                        snapshot_id=target.snapshot_id,
                        status="SKIPPED",
                        reason="동일 merchant/snapshot에 아직 읽지 않은 리마인드 알림이 있어 중복 생성을 건너뛰었습니다.",
                    )
                )
                skipped_count += 1
                continue

            result_item = ProWeeklyReportDeliveryRunItem(
                delivery_run_id=reminder_run.id,
                merchant_id=target.merchant_id,
                snapshot_id=target.snapshot_id,
                status="SENT",
                reason="미확인 Weekly Report 내부 알림 리마인드를 생성했습니다.",
            )
            db.add(result_item)
            db.flush()
            db.add(
                ProWeeklyReportInAppNotification(
                    merchant_id=target.merchant_id,
                    snapshot_id=target.snapshot_id,
                    delivery_run_id=reminder_run.id,
                    delivery_run_item_id=result_item.id,
                    title="Weekly Report 확인 리마인드",
                    message="아직 확인하지 않은 Weekly Report가 있습니다. BreadGo Pro에서 확인해 주세요.",
                    status="UNREAD",
                    created_at=datetime.now(timezone.utc),
                )
            )
            sent_count += 1
        except Exception as exc:
            db.add(
                ProWeeklyReportDeliveryRunItem(
                    delivery_run_id=reminder_run.id,
                    merchant_id=target.merchant_id,
                    snapshot_id=target.snapshot_id,
                    status="FAILED",
                    reason=str(exc),
                )
            )
            failed_count += 1

    reminder_run.ready_count = sent_count
    reminder_run.skipped_count = skipped_count
    reminder_run.failed_count = failed_count
    if failed_count and sent_count:
        reminder_run.status = "PARTIAL"
        reminder_run.message = "일부 Weekly Report 리마인드 mock delivery가 실패했습니다."
    elif failed_count and not sent_count:
        reminder_run.status = "FAILED"
        reminder_run.message = "Weekly Report 리마인드 mock delivery가 실패했습니다."
    else:
        reminder_run.status = "COMPLETED"
        reminder_run.message = "Weekly Report 리마인드 mock delivery가 완료되었습니다. 실제 외부 발송은 하지 않았습니다."
    reminder_run.completed_at = datetime.now(timezone.utc)
    db.commit()

    refreshed = db.scalar(
        select(ProWeeklyReportDeliveryRun)
        .where(ProWeeklyReportDeliveryRun.id == reminder_run.id)
        .options(selectinload(ProWeeklyReportDeliveryRun.items))
    )
    if refreshed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report delivery run not found.")
    return _delivery_run_to_read(refreshed)


def _weekly_report_notification_to_read(
    notification: ProWeeklyReportInAppNotification,
) -> ProWeeklyReportInAppNotificationRead:
    return ProWeeklyReportInAppNotificationRead(
        notification_id=notification.id,
        snapshot_id=notification.snapshot_id,
        title=notification.title,
        message=notification.message,
        status=notification.status,
        created_at=notification.created_at,
        read_at=notification.read_at,
    )


def _admin_weekly_report_notification_to_read(
    notification: ProWeeklyReportInAppNotification,
) -> AdminProWeeklyReportNotificationRead:
    return AdminProWeeklyReportNotificationRead(
        notification_id=notification.id,
        merchant_id=notification.merchant_id,
        snapshot_id=notification.snapshot_id,
        delivery_run_id=notification.delivery_run_id,
        title=notification.title,
        message=notification.message,
        status=notification.status,
        created_at=notification.created_at,
        read_at=notification.read_at,
    )


def _weekly_report_notification_filters(
    merchant_id: UUID | None = None,
    status_filter: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list:
    conditions = []
    if merchant_id is not None:
        conditions.append(ProWeeklyReportInAppNotification.merchant_id == merchant_id)
    if status_filter is not None:
        if status_filter not in {"UNREAD", "READ"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="status는 UNREAD 또는 READ만 가능합니다.")
        conditions.append(ProWeeklyReportInAppNotification.status == status_filter)
    if date_from is not None:
        conditions.append(
            ProWeeklyReportInAppNotification.created_at
            >= datetime.combine(date_from, time.min, tzinfo=KST).astimezone(timezone.utc)
        )
    if date_to is not None:
        conditions.append(
            ProWeeklyReportInAppNotification.created_at
            < (datetime.combine(date_to, time.min, tzinfo=KST) + timedelta(days=1)).astimezone(timezone.utc)
        )
    return conditions


def get_admin_weekly_report_notification_summary(
    db: Session,
    merchant_id: UUID | None = None,
    status_filter: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> AdminProWeeklyReportNotificationSummaryRead:
    conditions = _weekly_report_notification_filters(
        merchant_id=merchant_id,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
    )
    notifications = list(db.scalars(select(ProWeeklyReportInAppNotification).where(*conditions)))
    total_count = len(notifications)
    unread_count = sum(1 for notification in notifications if notification.status == "UNREAD")
    read_count = sum(1 for notification in notifications if notification.status == "READ")
    latest_created_at = max((notification.created_at for notification in notifications), default=None)
    latest_read_at = max(
        (notification.read_at for notification in notifications if notification.read_at is not None),
        default=None,
    )
    return AdminProWeeklyReportNotificationSummaryRead(
        total_count=total_count,
        unread_count=unread_count,
        read_count=read_count,
        read_rate=round((read_count / total_count) * 100, 1) if total_count else 0.0,
        latest_created_at=latest_created_at,
        latest_read_at=latest_read_at,
    )


def list_admin_weekly_report_notifications(
    db: Session,
    merchant_id: UUID | None = None,
    status_filter: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 100,
) -> AdminProWeeklyReportNotificationListRead:
    conditions = _weekly_report_notification_filters(
        merchant_id=merchant_id,
        status_filter=status_filter,
        date_from=date_from,
        date_to=date_to,
    )
    bounded_limit = max(1, min(limit, 200))
    notifications = list(
        db.scalars(
            select(ProWeeklyReportInAppNotification)
            .where(*conditions)
            .order_by(ProWeeklyReportInAppNotification.created_at.desc())
            .limit(bounded_limit)
        )
    )
    return AdminProWeeklyReportNotificationListRead(
        notifications=[_admin_weekly_report_notification_to_read(notification) for notification in notifications]
    )


def list_merchant_weekly_report_notifications(
    db: Session,
    merchant: Merchant,
    limit: int = 50,
) -> MerchantProWeeklyReportNotificationListRead:
    bounded_limit = max(1, min(limit, 100))
    notifications = list(
        db.scalars(
            select(ProWeeklyReportInAppNotification)
            .where(ProWeeklyReportInAppNotification.merchant_id == merchant.id)
            .order_by(ProWeeklyReportInAppNotification.created_at.desc())
            .limit(bounded_limit)
        )
    )
    return MerchantProWeeklyReportNotificationListRead(
        notifications=[_weekly_report_notification_to_read(notification) for notification in notifications]
    )


def get_merchant_weekly_report_unread_count(
    db: Session,
    merchant: Merchant,
) -> MerchantProWeeklyReportUnreadCountRead:
    unread_count = db.scalar(
        select(func.count())
        .select_from(ProWeeklyReportInAppNotification)
        .where(
            ProWeeklyReportInAppNotification.merchant_id == merchant.id,
            ProWeeklyReportInAppNotification.status == "UNREAD",
        )
    )
    return MerchantProWeeklyReportUnreadCountRead(unread_count=unread_count or 0)


def mark_merchant_weekly_report_notification_read(
    db: Session,
    merchant: Merchant,
    notification_id: UUID,
) -> ProWeeklyReportInAppNotificationRead:
    notification = db.scalar(
        select(ProWeeklyReportInAppNotification).where(
            ProWeeklyReportInAppNotification.id == notification_id,
            ProWeeklyReportInAppNotification.merchant_id == merchant.id,
        )
    )
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report notification not found.")
    notification.status = "READ"
    notification.read_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(notification)
    return _weekly_report_notification_to_read(notification)


def mark_all_merchant_weekly_report_notifications_read(
    db: Session,
    merchant: Merchant,
) -> MerchantProWeeklyReportReadAllResultRead:
    notifications = list(
        db.scalars(
            select(ProWeeklyReportInAppNotification).where(
                ProWeeklyReportInAppNotification.merchant_id == merchant.id,
                ProWeeklyReportInAppNotification.status == "UNREAD",
            )
        )
    )
    now = datetime.now(timezone.utc)
    for notification in notifications:
        notification.status = "READ"
        notification.read_at = now
    db.commit()
    return MerchantProWeeklyReportReadAllResultRead(updated_count=len(notifications), unread_count=0)


def build_admin_pro_operations_summary(db: Session) -> AdminProOperationsSummaryRead:
    now = datetime.now(timezone.utc)
    recent_start = now - timedelta(days=7)

    latest_batch = db.scalar(
        select(ProWeeklyReportBatchRun).order_by(ProWeeklyReportBatchRun.created_at.desc())
    )
    recent_batch_runs = list(
        db.scalars(select(ProWeeklyReportBatchRun).where(ProWeeklyReportBatchRun.created_at >= recent_start))
    )
    failed_batch_count = sum(1 for run in recent_batch_runs if run.status == "FAILED")
    partial_batch_count = sum(1 for run in recent_batch_runs if run.status == "PARTIAL")
    batch_summary = AdminProOperationsBatchSummaryRead(
        latest_status=latest_batch.status if latest_batch else None,
        latest_created_at=latest_batch.created_at if latest_batch else None,
        latest_run_type=latest_batch.run_type if latest_batch else None,
        latest_total_count=latest_batch.target_merchant_count if latest_batch else 0,
        latest_success_count=latest_batch.success_count if latest_batch else 0,
        latest_failed_count=latest_batch.failed_count if latest_batch else 0,
        latest_skipped_count=latest_batch.skipped_count if latest_batch else 0,
        recent_7_days_run_count=len(recent_batch_runs),
        recent_7_days_failed_or_partial_count=failed_batch_count + partial_batch_count,
    )

    latest_delivery = db.scalar(
        select(ProWeeklyReportDeliveryRun)
        .options(selectinload(ProWeeklyReportDeliveryRun.items))
        .order_by(ProWeeklyReportDeliveryRun.created_at.desc())
    )
    latest_delivery_items = latest_delivery.items if latest_delivery else []
    latest_sent_count = sum(1 for item in latest_delivery_items if item.status == "SENT")
    recent_delivery_runs = list(
        db.scalars(select(ProWeeklyReportDeliveryRun).where(ProWeeklyReportDeliveryRun.created_at >= recent_start))
    )
    failed_delivery_count = sum(1 for run in recent_delivery_runs if run.status in {"FAILED", "PARTIAL"})
    delivery_summary = AdminProOperationsDeliverySummaryRead(
        latest_status=latest_delivery.status if latest_delivery else None,
        latest_run_type=latest_delivery.run_type if latest_delivery else None,
        latest_channel=latest_delivery.channel if latest_delivery else None,
        latest_created_at=latest_delivery.created_at if latest_delivery else None,
        latest_total_count=latest_delivery.total_count if latest_delivery else 0,
        latest_ready_count=sum(1 for item in latest_delivery_items if item.status == "READY"),
        latest_sent_count=latest_sent_count,
        latest_skipped_count=latest_delivery.skipped_count if latest_delivery else 0,
        latest_failed_count=latest_delivery.failed_count if latest_delivery else 0,
    )

    notifications = list(db.scalars(select(ProWeeklyReportInAppNotification)))
    total_notifications = len(notifications)
    unread_count = sum(1 for notification in notifications if notification.status == "UNREAD")
    read_count = sum(1 for notification in notifications if notification.status == "READ")
    latest_created_at = max((notification.created_at for notification in notifications), default=None)
    latest_read_at = max(
        (notification.read_at for notification in notifications if notification.read_at is not None),
        default=None,
    )
    reminder_notifications = [notification for notification in notifications if "리마인드" in notification.title]
    latest_reminder_at = max((notification.created_at for notification in reminder_notifications), default=None)
    unread_reminder_count = sum(1 for notification in reminder_notifications if notification.status == "UNREAD")
    notification_summary = AdminProOperationsNotificationSummaryRead(
        total_count=total_notifications,
        read_count=read_count,
        unread_count=unread_count,
        read_rate=round((read_count / total_notifications) * 100, 1) if total_notifications else 0.0,
        latest_created_at=latest_created_at,
        latest_read_at=latest_read_at,
        latest_reminder_at=latest_reminder_at,
        unread_reminder_count=unread_reminder_count,
    )

    attention_messages: list[str] = []
    if latest_batch and latest_batch.status in {"FAILED", "PARTIAL"}:
        attention_messages.append("최근 Weekly Report batch에 실패 또는 부분 실패가 있습니다.")
    if latest_delivery and latest_delivery.status in {"FAILED", "PARTIAL"}:
        attention_messages.append("최근 delivery run에 실패 항목이 있습니다.")
    if unread_count > 0:
        attention_messages.append("미확인 Weekly Report 알림이 남아 있습니다.")
    if failed_batch_count > 0:
        attention_messages.append("최근 7일 내 실패한 Weekly Report batch가 있습니다.")
    if latest_reminder_at is not None and unread_count > 0:
        attention_messages.append("최근 리마인드 이후에도 읽지 않은 Weekly Report 알림이 남아 있습니다.")

    attention_summary = AdminProOperationsAttentionSummaryRead(
        failed_batch_count=failed_batch_count,
        partial_batch_count=partial_batch_count,
        failed_delivery_count=failed_delivery_count,
        unread_notification_count=unread_count,
        needs_attention=bool(attention_messages),
        attention_messages=attention_messages,
    )

    return AdminProOperationsSummaryRead(
        batch=batch_summary,
        delivery=delivery_summary,
        notifications=notification_summary,
        attention=attention_summary,
    )


def preview_admin_weekly_report_batch_run(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
) -> AdminWeeklyReportBatchPreviewRead:
    default_start, default_end = _default_report_range()
    resolved_start = start_date or default_start
    resolved_end = end_date or default_end
    target_merchant_count = db.scalar(select(func.count()).select_from(Merchant)) or 0
    return AdminWeeklyReportBatchPreviewRead(
        start_date=resolved_start,
        end_date=resolved_end,
        target_merchant_count=target_merchant_count,
        would_create_or_update_count=target_merchant_count,
        message=(
            f"{target_merchant_count}개 가맹점의 Weekly Report snapshot을 "
            "생성하거나 기존 동일 기간 snapshot을 업데이트할 예정입니다."
        ),
    )


def create_admin_weekly_report_batch_run(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
    run_type: str = "SCHEDULE_PREP",
    skip_if_completed: bool = False,
) -> ProWeeklyReportBatchRunRead:
    preview = preview_admin_weekly_report_batch_run(db, start_date=start_date, end_date=end_date)
    merchants = list(db.scalars(select(Merchant).order_by(Merchant.created_at.asc())))
    if skip_if_completed:
        existing_completed = db.scalar(
            select(ProWeeklyReportBatchRun)
            .where(
                ProWeeklyReportBatchRun.run_type == run_type,
                ProWeeklyReportBatchRun.status == "COMPLETED",
                ProWeeklyReportBatchRun.start_date == preview.start_date,
                ProWeeklyReportBatchRun.end_date == preview.end_date,
            )
            .order_by(ProWeeklyReportBatchRun.created_at.desc())
        )
        if existing_completed is not None:
            skipped_run = ProWeeklyReportBatchRun(
                run_type=run_type,
                status="SKIPPED",
                start_date=preview.start_date,
                end_date=preview.end_date,
                target_merchant_count=len(merchants),
                success_count=0,
                failed_count=0,
                skipped_count=len(merchants),
                message="동일 기간에 이미 완료된 SCHEDULED batch run이 있어 중복 실행하지 않았습니다.",
                created_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
            )
            db.add(skipped_run)
            db.commit()
            refreshed_skipped = db.scalar(
                select(ProWeeklyReportBatchRun)
                .where(ProWeeklyReportBatchRun.id == skipped_run.id)
                .options(selectinload(ProWeeklyReportBatchRun.items))
            )
            if refreshed_skipped is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report batch run not found.")
            return _batch_run_to_read(refreshed_skipped)

    batch_run = ProWeeklyReportBatchRun(
        run_type=run_type,
        status="STARTED",
        start_date=preview.start_date,
        end_date=preview.end_date,
        target_merchant_count=len(merchants),
        success_count=0,
        failed_count=0,
        skipped_count=0,
        message="전체 가맹점 Weekly Report 배치 실행을 시작했습니다.",
        created_at=datetime.now(timezone.utc),
    )
    db.add(batch_run)
    db.flush()

    success_count = 0
    failed_count = 0
    skipped_count = 0

    if not merchants:
        batch_run.status = "COMPLETED"
        batch_run.message = "대상 가맹점이 없어 실행할 Weekly Report 배치가 없습니다."
        batch_run.completed_at = datetime.now(timezone.utc)
        db.commit()
    else:
        for merchant in merchants:
            try:
                snapshot_result = create_current_week_snapshot(
                    db,
                    merchant,
                    start_date=preview.start_date,
                    end_date=preview.end_date,
                )
                db.add(
                    ProWeeklyReportBatchRunItem(
                        batch_run_id=batch_run.id,
                        merchant_id=merchant.id,
                        snapshot_id=snapshot_result.snapshot_id,
                        status="SUCCESS",
                        message=snapshot_result.message,
                    )
                )
                success_count += 1
            except Exception as exc:
                db.add(
                    ProWeeklyReportBatchRunItem(
                        batch_run_id=batch_run.id,
                        merchant_id=merchant.id,
                        status="FAILED",
                        message=str(exc),
                    )
                )
                failed_count += 1

        if failed_count and success_count:
            batch_run.status = "PARTIAL"
            batch_run.message = "일부 가맹점 Weekly Report 배치가 실패했습니다."
        elif failed_count and not success_count:
            batch_run.status = "FAILED"
            batch_run.message = "전체 가맹점 Weekly Report 배치가 실패했습니다."
        else:
            batch_run.status = "COMPLETED"
            batch_run.message = "전체 가맹점 Weekly Report 배치가 완료되었습니다."

        batch_run.success_count = success_count
        batch_run.failed_count = failed_count
        batch_run.skipped_count = skipped_count
        batch_run.completed_at = datetime.now(timezone.utc)
        db.commit()

    refreshed = db.scalar(
        select(ProWeeklyReportBatchRun)
        .where(ProWeeklyReportBatchRun.id == batch_run.id)
        .options(selectinload(ProWeeklyReportBatchRun.items))
    )
    if refreshed is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report batch run not found.")
    return _batch_run_to_read(refreshed)


def list_weekly_report_history(
    db: Session,
    merchant: Merchant,
    limit: int = 30,
) -> MerchantProWeeklyReportHistoryRead:
    bounded_limit = max(1, min(limit, 30))
    snapshots = list(
        db.scalars(
            select(ProWeeklyReportSnapshot)
            .where(ProWeeklyReportSnapshot.merchant_id == merchant.id)
            .options(selectinload(ProWeeklyReportSnapshot.insights))
            .order_by(ProWeeklyReportSnapshot.end_date.desc(), ProWeeklyReportSnapshot.created_at.desc())
            .limit(bounded_limit)
        )
    )
    return MerchantProWeeklyReportHistoryRead(
        snapshots=[_weekly_snapshot_to_read(snapshot) for snapshot in snapshots]
    )


def get_weekly_report_snapshot(
    db: Session,
    merchant: Merchant,
    snapshot_id: UUID,
) -> ProWeeklyReportSnapshotRead:
    snapshot = db.scalar(
        select(ProWeeklyReportSnapshot)
        .where(
            ProWeeklyReportSnapshot.id == snapshot_id,
            ProWeeklyReportSnapshot.merchant_id == merchant.id,
        )
        .options(selectinload(ProWeeklyReportSnapshot.insights))
    )
    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weekly report snapshot not found.")
    return _weekly_snapshot_to_read(snapshot)


def weekly_report_snapshot_to_csv(snapshot: ProWeeklyReportSnapshotRead) -> str:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["key", "value"])
    writer.writerow(["start_date", snapshot.start_date.isoformat()])
    writer.writerow(["end_date", snapshot.end_date.isoformat()])
    writer.writerow(["total_sales_amount", snapshot.total_sales_amount])
    writer.writerow(["total_reservation_count", snapshot.total_reservation_count])
    writer.writerow(["total_picked_up_count", snapshot.total_picked_up_count])
    writer.writerow(["total_cancelled_count", snapshot.total_cancelled_count])
    writer.writerow(["total_saved_quantity", snapshot.total_saved_quantity])
    writer.writerow(["average_unresolved_alert_count", snapshot.average_unresolved_alert_count])
    writer.writerow(["high_severity_alert_count", snapshot.high_severity_alert_count])
    writer.writerow(["total_recommendation_action_count", snapshot.total_recommendation_action_count])
    writer.writerow(["total_inventory_event_count", snapshot.total_inventory_event_count])
    writer.writerow(["pos_sync_issue_count", snapshot.pos_sync_issue_count])
    writer.writerow(["csv_import_error_count", snapshot.csv_import_error_count])
    writer.writerow([])
    writer.writerow(["insight_title", "insight_message", "severity"])
    for insight in snapshot.insights:
        writer.writerow([insight.title or "", insight.message, insight.severity or "INFO"])
    return output.getvalue()


def weekly_report_snapshot_to_text(snapshot: ProWeeklyReportSnapshotRead) -> str:
    if snapshot.text_summary:
        return snapshot.text_summary

    insight_lines = "\n".join(
        f"- {insight.title or '운영 인사이트'}: {insight.message}" for insight in snapshot.insights
    )
    if not insight_lines:
        insight_lines = "- 표시할 인사이트가 없습니다."

    return "\n".join(
        [
            "BreadGo Pro 저장된 주간 운영 리포트",
            f"기간: {snapshot.start_date.isoformat()} ~ {snapshot.end_date.isoformat()}",
            "",
            "[저장된 운영 요약]",
            f"- 총 매출: {int(snapshot.total_sales_amount):,}원",
            f"- 예약 수: {snapshot.total_reservation_count}건",
            f"- 픽업 완료: {snapshot.total_picked_up_count}건",
            f"- 취소: {snapshot.total_cancelled_count}건",
            f"- 폐기 절감: {snapshot.total_saved_quantity}개",
            f"- 평균 미해결 알림: {snapshot.average_unresolved_alert_count}건",
            f"- HIGH 알림: {snapshot.high_severity_alert_count}건",
            f"- 추천 액션: {snapshot.total_recommendation_action_count}건",
            "",
            "[저장된 인사이트]",
            insight_lines,
            "",
            "이 요약은 저장된 BreadGo Pro rule-based 운영 리포트입니다.",
        ]
    )
