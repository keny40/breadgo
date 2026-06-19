from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.merchant import Merchant
from app.models.payment import PaymentStatus
from app.models.product import Product
from app.models.product_event import ProductEvent
from app.models.recommendation_usage import RecommendationUsage
from app.models.reservation import Reservation, ReservationStatus
from app.models.store import Store
from app.schemas.pro_product_funnel import MerchantProProductFunnelRead, ProProductFunnelSummary
from app.services.pro_recommendation_service import _rate

ZERO = Decimal("0.00")


def _funnel_rate(numerator: int, denominator: int) -> float:
    return min(100.0, _rate(numerator, denominator))


def build_merchant_pro_product_funnel(db: Session, merchant: Merchant) -> MerchantProProductFunnelRead:
    period_days = 7
    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=period_days)

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
        return MerchantProProductFunnelRead(
            period_days=period_days,
            total_detail_views=0,
            total_reservation_starts=0,
            total_reservations=0,
            total_paid_count=0,
            total_picked_up_count=0,
            detail_to_reservation_rate=0.0,
            product_funnel_summaries=[],
        )

    events = list(
        db.scalars(
            select(ProductEvent).where(
                ProductEvent.product_id.in_(product_ids),
                ProductEvent.created_at >= period_start,
                ProductEvent.created_at <= now,
            )
        )
    )
    reservations = list(
        db.scalars(
            select(Reservation)
            .where(
                Reservation.product_id.in_(product_ids),
                Reservation.created_at >= period_start,
                Reservation.created_at <= now,
            )
            .options(selectinload(Reservation.payment))
        )
    )
    recommendation_product_ids = set(
        db.scalars(
            select(RecommendationUsage.created_product_id).where(
                RecommendationUsage.merchant_id == merchant.id,
                RecommendationUsage.created_product_id.is_not(None),
            )
        )
    )

    detail_views = Counter(event.product_id for event in events if event.event_type == "DETAIL_VIEW")
    reservation_starts = Counter(event.product_id for event in events if event.event_type == "RESERVATION_STARTED")
    reservations_by_product: dict[object, list[Reservation]] = defaultdict(list)
    for reservation in reservations:
        reservations_by_product[reservation.product_id].append(reservation)

    summaries: list[ProProductFunnelSummary] = []
    total_detail_views = 0
    total_reservation_starts = 0
    total_reservations = 0
    total_paid_count = 0
    total_picked_up_count = 0

    for product in products:
        product_reservations = reservations_by_product.get(product.id, [])
        reservation_count = len(product_reservations)
        paid_count = sum(
            1
            for reservation in product_reservations
            if reservation.payment and reservation.payment.status == PaymentStatus.PAID
        )
        picked_up_count = sum(
            1
            for reservation in product_reservations
            if reservation.status == ReservationStatus.PICKED_UP
        )
        paid_amount = sum(
            (
                reservation.product_amount
                for reservation in product_reservations
                if reservation.payment and reservation.payment.status == PaymentStatus.PAID
            ),
            ZERO,
        )
        product_detail_views = detail_views[product.id]
        product_reservation_starts = reservation_starts[product.id]
        conversion_rate = _funnel_rate(reservation_count, product_detail_views)
        paid_conversion_rate = _funnel_rate(paid_count, product_detail_views)
        pickup_conversion_rate = _funnel_rate(picked_up_count, product_detail_views)
        attention_label = "정상"
        if product_detail_views >= 3 and conversion_rate < 20:
            attention_label = "조회는 많지만 예약이 낮은 상품"
        elif product_detail_views == 0 and reservation_count == 0:
            attention_label = "고객 반응 데이터 부족"
        elif conversion_rate >= 50:
            attention_label = "예약 전환 우수"

        total_detail_views += product_detail_views
        total_reservation_starts += product_reservation_starts
        total_reservations += reservation_count
        total_paid_count += paid_count
        total_picked_up_count += picked_up_count

        summaries.append(
            ProProductFunnelSummary(
                product_id=product.id,
                product_name=product.name,
                store_id=product.store_id,
                store_name=product.store.name if product.store else "매장 정보 없음",
                detail_views=product_detail_views,
                reservation_started_count=product_reservation_starts,
                reservations=reservation_count,
                paid_count=paid_count,
                picked_up_count=picked_up_count,
                conversion_rate=conversion_rate,
                paid_conversion_rate=paid_conversion_rate,
                pickup_conversion_rate=pickup_conversion_rate,
                paid_amount=paid_amount,
                from_recommendation=product.id in recommendation_product_ids,
                attention_label=attention_label,
            )
        )

    summaries.sort(key=lambda item: (-item.detail_views, item.conversion_rate, item.product_name))

    return MerchantProProductFunnelRead(
        period_days=period_days,
        total_detail_views=total_detail_views,
        total_reservation_starts=total_reservation_starts,
        total_reservations=total_reservations,
        total_paid_count=total_paid_count,
        total_picked_up_count=total_picked_up_count,
        detail_to_reservation_rate=_funnel_rate(total_reservations, total_detail_views),
        product_funnel_summaries=summaries,
    )
