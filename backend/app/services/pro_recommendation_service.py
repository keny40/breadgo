from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from math import ceil

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.merchant import Merchant
from app.models.payment import PaymentStatus
from app.models.product import Product
from app.models.reservation import Reservation, ReservationStatus
from app.models.store import Store
from app.schemas.pro_recommendation import MerchantProRecommendationsRead, ProRecommendationRead

ZERO = Decimal("0.00")


@dataclass
class RecommendationAggregate:
    reserved_quantity: int = 0
    picked_up_quantity: int = 0
    cancelled_quantity: int = 0
    paid_count: int = 0
    picked_up_count: int = 0
    cancelled_count: int = 0


def _rate(numerator: int | Decimal, denominator: int | Decimal) -> float:
    if denominator == 0:
        return 0.0
    return round(float(numerator) / float(denominator) * 100, 1)


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("1.00"), rounding=ROUND_HALF_UP)


def _lower_price(price: Decimal) -> Decimal:
    return _money(max(Decimal("100.00"), price * Decimal("0.90")))


def _raise_price(price: Decimal, original_price: Decimal) -> Decimal:
    return _money(min(original_price, price * Decimal("1.05")))


def _confidence(total_events: int, sell_through_rate: float, pickup_completion_rate: float, cancellation_rate: float) -> str:
    if total_events < 3:
        return "LOW"
    if total_events >= 6 and sell_through_rate >= 80 and pickup_completion_rate >= 80 and cancellation_rate <= 20:
        return "HIGH"
    if total_events >= 4:
        return "MEDIUM"
    return "LOW"


def _recommended_base_stock(aggregate: RecommendationAggregate) -> int:
    daily_pickup_average = aggregate.picked_up_quantity / 7
    daily_reserved_average = aggregate.reserved_quantity / 7
    base = max(daily_pickup_average, daily_reserved_average)
    return max(1, ceil(base))


def build_merchant_pro_recommendations(db: Session, merchant: Merchant) -> MerchantProRecommendationsRead:
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

    reservations = list(
        db.scalars(
            select(Reservation)
            .join(Store, Reservation.store_id == Store.id)
            .where(
                Store.merchant_id == merchant.id,
                Reservation.created_at >= period_start,
                Reservation.created_at <= now,
            )
            .options(selectinload(Reservation.payment))
        )
    )

    aggregates: dict[object, RecommendationAggregate] = defaultdict(RecommendationAggregate)
    for reservation in reservations:
        aggregate = aggregates[reservation.product_id]
        if reservation.status == ReservationStatus.CANCELLED:
            aggregate.cancelled_quantity += reservation.quantity
            aggregate.cancelled_count += 1
            continue

        aggregate.reserved_quantity += reservation.quantity
        if reservation.payment and reservation.payment.status == PaymentStatus.PAID:
            aggregate.paid_count += 1
        if reservation.status == ReservationStatus.PICKED_UP:
            aggregate.picked_up_quantity += reservation.quantity
            aggregate.picked_up_count += 1

    recommendations: list[ProRecommendationRead] = []
    for product in products:
        aggregate = aggregates[product.id]
        registered_quantity = product.quantity + aggregate.reserved_quantity
        sell_through_rate = _rate(aggregate.reserved_quantity, registered_quantity)
        pickup_completion_rate = _rate(aggregate.picked_up_count, aggregate.paid_count)
        cancellation_rate = _rate(aggregate.cancelled_count, aggregate.paid_count + aggregate.cancelled_count)
        total_events = aggregate.paid_count + aggregate.cancelled_count
        confidence_label = _confidence(total_events, sell_through_rate, pickup_completion_rate, cancellation_rate)

        base_stock = _recommended_base_stock(aggregate)
        recommended_stock = max(1, base_stock)
        recommended_price = product.discount_price
        recommendation_type = "KEEP"
        message = "최근 7일 데이터 기준으로 현재 재고와 할인가를 유지해도 좋습니다."

        if total_events < 3:
            recommended_stock = max(1, product.quantity or 1)
            message = "데이터가 적어 보수적으로 현재 설정을 참고하세요. 더 많은 판매 데이터가 쌓이면 추천 정확도가 올라갑니다."
        elif cancellation_rate >= 30:
            recommendation_type = "DECREASE_STOCK"
            recommended_stock = max(1, min(product.quantity or base_stock, base_stock))
            message = "취소율이 높아 재고를 늘리기보다 보수적으로 운영하는 것을 권장합니다."
        elif sell_through_rate >= 80 and pickup_completion_rate >= 80:
            recommendation_type = "INCREASE_STOCK"
            recommended_stock = max(product.quantity + 1, ceil(base_stock * 1.2))
            recommended_price = _raise_price(product.discount_price, product.original_price)
            if recommended_price > product.discount_price:
                recommendation_type = "RAISE_PRICE"
                message = "판매율과 픽업 완료율이 높아 재고를 소폭 늘리고 할인가를 약간 올려도 되는 흐름입니다."
            else:
                message = "판매율과 픽업 완료율이 높아 다음 등록 시 재고를 소폭 늘리는 것을 권장합니다."
        elif sell_through_rate <= 30:
            recommended_stock = max(1, min(product.quantity or base_stock, base_stock))
            if product.discount_price > product.original_price * Decimal("0.50"):
                recommendation_type = "LOWER_PRICE"
                recommended_price = _lower_price(product.discount_price)
                message = "판매율이 낮아 할인가를 10% 범위에서 낮춰 테스트하는 것을 권장합니다."
            else:
                recommendation_type = "DECREASE_STOCK"
                message = "판매율이 낮고 이미 할인 폭이 커서 재고를 줄여 테스트하는 것을 권장합니다."
        elif sell_through_rate >= 60 and pickup_completion_rate >= 70:
            recommendation_type = "INCREASE_STOCK"
            recommended_stock = max(product.quantity, ceil(base_stock * 1.1))
            message = "판매 흐름이 안정적입니다. 재고를 소폭 늘려도 되는 후보 상품입니다."

        recommendations.append(
            ProRecommendationRead(
                product_id=product.id,
                product_name=product.name,
                store_id=product.store_id,
                store_name=product.store.name if product.store else "매장 정보 없음",
                recent_reserved_quantity=aggregate.reserved_quantity,
                recent_picked_up_quantity=aggregate.picked_up_quantity,
                recent_cancelled_quantity=aggregate.cancelled_quantity,
                current_stock_quantity=product.quantity,
                sell_through_rate=sell_through_rate,
                pickup_completion_rate=pickup_completion_rate,
                recommended_stock_quantity=recommended_stock,
                current_discount_price=product.discount_price,
                recommended_discount_price=_money(recommended_price),
                recommendation_type=recommendation_type,
                recommendation_message=message,
                confidence_label=confidence_label,
            )
        )

    priority = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    recommendations.sort(
        key=lambda item: (
            priority.get(item.confidence_label, 3),
            -item.sell_through_rate,
            item.product_name,
        )
    )

    return MerchantProRecommendationsRead(
        period_days=period_days,
        note="최근 7일 판매 데이터를 기준으로 계산한 rule-based 추천입니다. 실제 AI 추천은 준비 단계입니다.",
        recommendations=recommendations,
    )

