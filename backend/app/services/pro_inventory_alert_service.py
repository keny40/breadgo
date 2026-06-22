from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.merchant import Merchant
from app.models.product import Product, ProductStatus
from app.models.product_event import ProductEvent
from app.models.product_inventory_event import ProductInventoryEvent
from app.models.reservation import Reservation, ReservationStatus
from app.models.store import Store
from app.schemas.pro_inventory_alert import MerchantProInventoryAlertsRead, ProInventoryAlertRead
from app.services.inventory_alert_action_service import latest_inventory_alert_actions_by_key


SEVERITY_RANK = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator * 100, 1)


def _recent_note(events: list[ProductInventoryEvent]) -> str | None:
    if not events:
        return None
    event = max(events, key=lambda item: item.created_at)
    delta = ""
    if event.quantity_delta is not None:
        delta = f" / 증감 {event.quantity_delta:+d}개"
    return f"최근 이력: {event.event_type}{delta}"


def _alert(
    *,
    product: Product,
    severity: str,
    alert_type: str,
    title: str,
    message: str,
    suggested_action: str,
    related_metric: str | None,
    recent_inventory_note: str | None,
    detected_at: datetime,
) -> ProInventoryAlertRead:
    return ProInventoryAlertRead(
        product_id=product.id,
        product_name=product.name,
        store_id=product.store_id,
        store_name=product.store.name if product.store else "매장 정보 없음",
        severity=severity,
        alert_type=alert_type,
        title=title,
        message=message,
        suggested_action=suggested_action,
        current_stock_quantity=product.quantity,
        related_metric=related_metric,
        recent_inventory_note=recent_inventory_note,
        detected_at=detected_at,
    )


def build_merchant_pro_inventory_alerts(
    db: Session,
    merchant: Merchant,
) -> MerchantProInventoryAlertsRead:
    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=7)

    products = list(
        db.scalars(
            select(Product)
            .join(Store, Product.store_id == Store.id)
            .where(Store.merchant_id == merchant.id)
            .options(selectinload(Product.store))
            .order_by(Product.updated_at.desc(), Product.created_at.desc())
        )
    )
    product_ids = [product.id for product in products]
    if not product_ids:
        return MerchantProInventoryAlertsRead(total_alerts=0, high_count=0, medium_count=0, low_count=0, alerts=[])
    latest_actions = latest_inventory_alert_actions_by_key(db, merchant)

    reservations = list(
        db.scalars(
            select(Reservation).where(
                Reservation.product_id.in_(product_ids),
                Reservation.created_at >= period_start,
                Reservation.created_at <= now,
            )
        )
    )
    product_events = list(
        db.scalars(
            select(ProductEvent).where(
                ProductEvent.product_id.in_(product_ids),
                ProductEvent.created_at >= period_start,
                ProductEvent.created_at <= now,
            )
        )
    )
    inventory_events = list(
        db.scalars(
            select(ProductInventoryEvent).where(
                ProductInventoryEvent.product_id.in_(product_ids),
                ProductInventoryEvent.created_at >= period_start,
                ProductInventoryEvent.created_at <= now,
            )
        )
    )

    detail_views = Counter(event.product_id for event in product_events if event.event_type == "DETAIL_VIEW")
    reservation_count = Counter(reservation.product_id for reservation in reservations)
    active_reservation_quantity = Counter()
    cancelled_events_by_product: dict[object, list[ProductInventoryEvent]] = defaultdict(list)
    inventory_events_by_product: dict[object, list[ProductInventoryEvent]] = defaultdict(list)

    for reservation in reservations:
        if reservation.status != ReservationStatus.CANCELLED:
            active_reservation_quantity[reservation.product_id] += reservation.quantity

    for event in inventory_events:
        inventory_events_by_product[event.product_id].append(event)
        if event.event_type == "RESERVATION_CANCELLED":
            cancelled_events_by_product[event.product_id].append(event)

    alerts: list[ProInventoryAlertRead] = []
    for product in products:
        note = _recent_note(inventory_events_by_product.get(product.id, []))
        views = detail_views[product.id]
        reservations_for_product = reservation_count[product.id]
        reserved_quantity = active_reservation_quantity[product.id]
        registered_quantity = product.quantity + reserved_quantity
        sell_through_rate = _rate(reserved_quantity, registered_quantity)
        view_to_reservation_rate = _rate(reservations_for_product, views)

        if product.quantity < 0:
            alerts.append(
                _alert(
                    product=product,
                    severity="HIGH",
                    alert_type="NEGATIVE_STOCK",
                    title="재고가 음수입니다",
                    message="상품 재고가 0보다 작습니다. 예약/동기화 충돌 가능성을 확인하세요.",
                    suggested_action="상품관리에서 재고를 즉시 보정하고 재고 이력을 확인하세요.",
                    related_metric=f"현재 재고 {product.quantity}개",
                    recent_inventory_note=note,
                    detected_at=now,
                )
            )

        if product.pickup_end_time < now and product.quantity > 0 and product.status == ProductStatus.ACTIVE:
            alerts.append(
                _alert(
                    product=product,
                    severity="MEDIUM",
                    alert_type="EXPIRED_WITH_STOCK",
                    title="판매 시간이 지났는데 재고가 남았습니다",
                    message="마감 시간이 지난 활성 상품에 재고가 남아 있습니다.",
                    suggested_action="상품을 숨김 처리하거나 오늘 판매 시간으로 다시 등록하세요.",
                    related_metric=f"남은 재고 {product.quantity}개",
                    recent_inventory_note=note,
                    detected_at=now,
                )
            )

        if views >= 5 and reservations_for_product <= 1:
            alerts.append(
                _alert(
                    product=product,
                    severity="MEDIUM",
                    alert_type="HIGH_VIEW_LOW_RESERVATION",
                    title="조회는 많지만 예약 전환이 낮습니다",
                    message="최근 7일 고객 조회가 충분하지만 예약 생성이 낮습니다.",
                    suggested_action="할인가, 대표 이미지, 수령 시간, 배송 조건을 점검하세요.",
                    related_metric=f"조회 {views}회 / 예약 {reservations_for_product}건 / 전환율 {view_to_reservation_rate}%",
                    recent_inventory_note=note,
                    detected_at=now,
                )
            )

        large_changes = [
            event
            for event in inventory_events_by_product.get(product.id, [])
            if event.quantity_delta is not None and abs(event.quantity_delta) >= 10
        ]
        if large_changes:
            largest = max(large_changes, key=lambda event: abs(event.quantity_delta or 0))
            alerts.append(
                _alert(
                    product=product,
                    severity="LOW",
                    alert_type="LARGE_STOCK_CHANGE",
                    title="큰 재고 변동이 감지되었습니다",
                    message="최근 재고 이력에서 큰 폭의 재고 변경이 있었습니다.",
                    suggested_action="CSV/POS/수동 수정 이력을 확인해 의도한 변경인지 점검하세요.",
                    related_metric=f"최대 변동 {largest.quantity_delta:+d}개",
                    recent_inventory_note=note,
                    detected_at=now,
                )
            )

        if product.status == ProductStatus.HIDDEN and product.quantity > 0 and cancelled_events_by_product.get(product.id):
            alerts.append(
                _alert(
                    product=product,
                    severity="MEDIUM",
                    alert_type="CANCEL_RESTORED_HIDDEN",
                    title="취소로 복구된 재고가 숨김 상품에 남아 있습니다",
                    message="예약 취소로 재고가 복구되었지만 상품이 고객에게 노출되지 않는 상태입니다.",
                    suggested_action="상품관리에서 다시 판매하거나 재고를 조정하세요.",
                    related_metric=f"숨김 재고 {product.quantity}개",
                    recent_inventory_note=note,
                    detected_at=now,
                )
            )

        if product.quantity <= 2 and views >= 3 and sell_through_rate >= 70:
            alerts.append(
                _alert(
                    product=product,
                    severity="LOW",
                    alert_type="LOW_STOCK_HIGH_DEMAND",
                    title="수요 대비 재고가 낮습니다",
                    message="조회/예약 흐름이 좋은데 남은 재고가 적습니다.",
                    suggested_action="추천 화면에서 다음 등록 재고를 소폭 늘릴지 확인하세요.",
                    related_metric=f"재고 {product.quantity}개 / 판매율 {sell_through_rate}%",
                    recent_inventory_note=note,
                    detected_at=now,
                )
            )

    alerts.sort(key=lambda item: (SEVERITY_RANK.get(item.severity, 3), item.product_name, item.alert_type))
    for alert in alerts:
        latest_action = latest_actions.get((alert.product_id, alert.alert_type))
        if latest_action is None:
            continue
        alert.latest_action_type = latest_action.action_type
        alert.latest_action_at = latest_action.created_at
        alert.is_acknowledged = latest_action.action_type in {"ACKNOWLEDGED", "ACTION_STARTED", "MARKED_RESOLVED", "DISMISSED"}
        alert.is_resolved = latest_action.action_type == "MARKED_RESOLVED"
    high_count = sum(1 for item in alerts if item.severity == "HIGH")
    medium_count = sum(1 for item in alerts if item.severity == "MEDIUM")
    low_count = sum(1 for item in alerts if item.severity == "LOW")
    return MerchantProInventoryAlertsRead(
        total_alerts=len(alerts),
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        alerts=alerts,
    )
