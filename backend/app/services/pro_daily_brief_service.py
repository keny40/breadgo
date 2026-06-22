from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.merchant import Merchant
from app.models.product_import import ProductImportBatch
from app.models.product_inventory_event import ProductInventoryEvent
from app.schemas.pro_daily_brief import MerchantProDailyBriefRead, ProDailyBriefTaskRead
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
