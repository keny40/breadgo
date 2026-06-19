from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from math import ceil

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.merchant import Merchant
from app.models.payment import PaymentStatus
from app.models.product import Product
from app.models.recommendation_usage import RecommendationUsage
from app.models.reservation import Reservation, ReservationStatus
from app.models.store import Store
from app.schemas.product import ProductDuplicateCreate
from app.schemas.pro_recommendation import (
    MerchantProRecommendationPerformanceRead,
    MerchantProRecommendationsRead,
    ProRecommendationDraftCreateRequest,
    ProRecommendationDraftCreateResponse,
    ProRecommendationRead,
    RecommendationTypeUsageSummary,
    RecommendationUsageRead,
)
from app.services.product_service import duplicate_product_for_merchant

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


def _find_recommendation(
    db: Session,
    merchant: Merchant,
    product_id,
) -> ProRecommendationRead:
    recommendations = build_merchant_pro_recommendations(db, merchant).recommendations
    for recommendation in recommendations:
        if recommendation.product_id == product_id:
            return recommendation
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found for product.")


def create_recommendation_draft(
    db: Session,
    merchant: Merchant,
    product_id,
    payload: ProRecommendationDraftCreateRequest,
) -> ProRecommendationDraftCreateResponse:
    recommendation = _find_recommendation(db, merchant, product_id)
    original_product = db.scalar(
        select(Product)
        .join(Store, Product.store_id == Store.id)
        .where(Product.id == product_id, Store.merchant_id == merchant.id)
    )
    if original_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    accepted_stock_quantity = (
        payload.accepted_stock_quantity
        if payload.accepted_stock_quantity is not None
        else recommendation.recommended_stock_quantity
    )
    accepted_discount_price = (
        _money(payload.accepted_discount_price)
        if payload.accepted_discount_price is not None
        else recommendation.recommended_discount_price
    )
    if accepted_stock_quantity < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="accepted_stock_quantity must be 0 or more.")
    if accepted_discount_price < ZERO:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="accepted_discount_price must be 0 or more.")
    if accepted_discount_price > original_product.original_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="accepted_discount_price cannot be greater than original price.",
        )
    stock_delta = accepted_stock_quantity - recommendation.recommended_stock_quantity
    discount_price_delta = _money(accepted_discount_price - recommendation.recommended_discount_price)
    adoption_type = "EXACT_ACCEPTED" if stock_delta == 0 and discount_price_delta == ZERO else "MODIFIED_ACCEPTED"

    created_product = duplicate_product_for_merchant(
        db,
        merchant,
        product_id,
        ProductDuplicateCreate(
            stock_quantity=accepted_stock_quantity,
            sale_starts_at=payload.accepted_sale_starts_at or now + timedelta(hours=1),
            sale_ends_at=payload.accepted_sale_ends_at or now + timedelta(hours=4),
            is_visible=payload.is_visible,
            name_suffix=payload.name_suffix or "추천",
        ),
    )
    created_product.discount_price = accepted_discount_price

    usage = RecommendationUsage(
        merchant_id=merchant.id,
        source_product_id=product_id,
        created_product_id=created_product.id,
        recommendation_type=recommendation.recommendation_type,
        confidence_label=recommendation.confidence_label,
        recommended_stock_quantity=recommendation.recommended_stock_quantity,
        recommended_discount_price=recommendation.recommended_discount_price,
        original_stock_quantity=original_product.quantity,
        original_discount_price=original_product.discount_price,
        accepted_stock_quantity=accepted_stock_quantity,
        accepted_discount_price=accepted_discount_price,
        stock_delta=stock_delta,
        discount_price_delta=discount_price_delta,
        adoption_type=adoption_type,
        draft_product_status="PUBLISHED" if payload.is_visible else "HIDDEN_DRAFT",
        published_at=datetime.now(timezone.utc) if payload.is_visible else None,
        action_type="DRAFT_CREATED",
    )
    db.add(usage)
    db.commit()
    db.refresh(usage)
    db.refresh(created_product)

    from app.schemas.product import ProductRead

    return ProRecommendationDraftCreateResponse(
        created_product=ProductRead.model_validate(created_product),
        usage_id=usage.id,
        recommendation=recommendation,
    )


def build_merchant_pro_recommendation_performance(
    db: Session,
    merchant: Merchant,
) -> MerchantProRecommendationPerformanceRead:
    usages = list(
        db.scalars(
            select(RecommendationUsage)
            .where(RecommendationUsage.merchant_id == merchant.id)
            .options(
                selectinload(RecommendationUsage.source_product),
                selectinload(RecommendationUsage.created_product),
            )
            .order_by(RecommendationUsage.created_at.desc())
        )
    )
    created_product_ids = [usage.created_product_id for usage in usages if usage.created_product_id is not None]
    reservations = []
    if created_product_ids:
        reservations = list(
            db.scalars(
                select(Reservation)
                .where(Reservation.product_id.in_(created_product_ids))
                .options(selectinload(Reservation.payment))
            )
        )

    reservations_by_product: dict[object, list[Reservation]] = defaultdict(list)
    for reservation in reservations:
        reservations_by_product[reservation.product_id].append(reservation)

    total_picked_up_quantity = 0
    total_paid_amount = ZERO
    reserved_after_publish_count = 0
    paid_after_publish_count = 0
    picked_up_after_publish_count = 0
    time_to_publish_minutes: list[float] = []
    sell_through_rates: list[float] = []
    exact_accept_count = 0
    modified_accept_count = 0
    stock_deltas: list[int] = []
    discount_price_deltas: list[Decimal] = []
    usage_type_summary: dict[str, RecommendationTypeUsageSummary] = {}
    recent_usages: list[RecommendationUsageRead] = []

    for usage in usages:
        accepted_stock_quantity = usage.accepted_stock_quantity
        if accepted_stock_quantity is None:
            accepted_stock_quantity = usage.recommended_stock_quantity
        accepted_discount_price = usage.accepted_discount_price
        if accepted_discount_price is None:
            accepted_discount_price = usage.recommended_discount_price
        stock_delta = usage.stock_delta
        if stock_delta is None:
            stock_delta = accepted_stock_quantity - usage.recommended_stock_quantity
        discount_price_delta = usage.discount_price_delta
        if discount_price_delta is None:
            discount_price_delta = _money(accepted_discount_price - usage.recommended_discount_price)
        adoption_type = usage.adoption_type
        if adoption_type is None:
            adoption_type = "EXACT_ACCEPTED" if stock_delta == 0 and discount_price_delta == ZERO else "MODIFIED_ACCEPTED"
        draft_product_status = usage.draft_product_status
        if draft_product_status is None:
            if usage.created_product and usage.created_product.status.value == "ACTIVE":
                draft_product_status = "PUBLISHED"
            elif usage.created_product and usage.created_product.status.value == "HIDDEN":
                draft_product_status = "HIDDEN_DRAFT"
            else:
                draft_product_status = "ARCHIVED"

        if adoption_type == "EXACT_ACCEPTED":
            exact_accept_count += 1
        elif adoption_type == "MODIFIED_ACCEPTED":
            modified_accept_count += 1
        stock_deltas.append(stock_delta)
        discount_price_deltas.append(discount_price_delta)

        product_reservations = reservations_by_product.get(usage.created_product_id, [])
        first_reserved_at = min((reservation.created_at for reservation in product_reservations), default=None)
        first_paid_at = min(
            (
                reservation.payment.paid_at
                for reservation in product_reservations
                if reservation.payment and reservation.payment.status == PaymentStatus.PAID and reservation.payment.paid_at
            ),
            default=None,
        )
        first_picked_up_at = min(
            (
                reservation.updated_at
                for reservation in product_reservations
                if reservation.status == ReservationStatus.PICKED_UP
            ),
            default=None,
        )
        if first_reserved_at and usage.first_reserved_at is None:
            usage.first_reserved_at = first_reserved_at
        if first_paid_at and usage.first_paid_at is None:
            usage.first_paid_at = first_paid_at
        if first_picked_up_at and usage.first_picked_up_at is None:
            usage.first_picked_up_at = first_picked_up_at

        reserved_quantity = sum(
            reservation.quantity
            for reservation in product_reservations
            if reservation.status != ReservationStatus.CANCELLED
        )
        picked_up_quantity = sum(
            reservation.quantity
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
        current_stock = usage.created_product.quantity if usage.created_product else 0
        registered_quantity = current_stock + reserved_quantity
        sell_through_rate = _rate(reserved_quantity, registered_quantity)
        if usage.created_product_id is not None:
            sell_through_rates.append(sell_through_rate)

        total_picked_up_quantity += picked_up_quantity
        total_paid_amount += paid_amount
        if first_reserved_at:
            reserved_after_publish_count += 1
        if first_paid_at:
            paid_after_publish_count += 1
        if first_picked_up_at:
            picked_up_after_publish_count += 1
        if usage.published_at:
            time_to_publish_minutes.append((usage.published_at - usage.created_at).total_seconds() / 60)

        summary = usage_type_summary.setdefault(
            usage.recommendation_type,
            RecommendationTypeUsageSummary(
                recommendation_type=usage.recommendation_type,
                count=0,
                picked_up_quantity=0,
                paid_amount=ZERO,
            ),
        )
        summary.count += 1
        summary.picked_up_quantity += picked_up_quantity
        summary.paid_amount += paid_amount

        if len(recent_usages) < 20:
            recent_usages.append(
                RecommendationUsageRead(
                    id=usage.id,
                    source_product_id=usage.source_product_id,
                    source_product_name=usage.source_product.name if usage.source_product else None,
                    created_product_id=usage.created_product_id,
                    created_product_name=usage.created_product.name if usage.created_product else None,
                    recommendation_type=usage.recommendation_type,
                    confidence_label=usage.confidence_label,
                    recommended_stock_quantity=usage.recommended_stock_quantity,
                    recommended_discount_price=usage.recommended_discount_price,
                    original_stock_quantity=usage.original_stock_quantity,
                    original_discount_price=usage.original_discount_price,
                    accepted_stock_quantity=accepted_stock_quantity,
                    accepted_discount_price=accepted_discount_price,
                    stock_delta=stock_delta,
                    discount_price_delta=discount_price_delta,
                    adoption_type=adoption_type,
                    draft_product_status=draft_product_status,
                    published_at=usage.published_at.isoformat() if usage.published_at else None,
                    first_reserved_at=first_reserved_at.isoformat() if first_reserved_at else None,
                    first_paid_at=first_paid_at.isoformat() if first_paid_at else None,
                    first_picked_up_at=first_picked_up_at.isoformat() if first_picked_up_at else None,
                    action_type=usage.action_type,
                    created_product_reserved_quantity=reserved_quantity,
                    created_product_picked_up_quantity=picked_up_quantity,
                    created_product_paid_amount=paid_amount,
                    created_product_sell_through_rate=sell_through_rate,
                    created_at=usage.created_at.isoformat(),
                )
            )

    average_sell_through_rate = round(sum(sell_through_rates) / len(sell_through_rates), 1) if sell_through_rates else 0.0
    accepted_count = exact_accept_count + modified_accept_count
    average_stock_delta = round(sum(stock_deltas) / len(stock_deltas), 1) if stock_deltas else 0.0
    average_discount_price_delta = (
        _money(sum(discount_price_deltas, ZERO) / Decimal(len(discount_price_deltas)))
        if discount_price_deltas
        else ZERO
    )
    db.commit()

    return MerchantProRecommendationPerformanceRead(
        total_recommendation_drafts=sum(1 for usage in usages if usage.action_type == "DRAFT_CREATED"),
        draft_created_count=sum(1 for usage in usages if usage.action_type == "DRAFT_CREATED"),
        published_from_recommendation_count=sum(
            1
            for usage in usages
            if usage.published_at is not None
            or (usage.draft_product_status == "PUBLISHED")
            or (usage.created_product and usage.created_product.status.value == "ACTIVE")
        ),
        publish_conversion_rate=_rate(
            sum(
                1
                for usage in usages
                if usage.published_at is not None
                or (usage.draft_product_status == "PUBLISHED")
                or (usage.created_product and usage.created_product.status.value == "ACTIVE")
            ),
            sum(1 for usage in usages if usage.action_type == "DRAFT_CREATED"),
        ),
        reserved_after_publish_count=reserved_after_publish_count,
        paid_after_publish_count=paid_after_publish_count,
        picked_up_after_publish_count=picked_up_after_publish_count,
        average_time_to_publish_minutes=round(sum(time_to_publish_minutes) / len(time_to_publish_minutes), 1)
        if time_to_publish_minutes
        else 0.0,
        used_recommendation_count=len(usages),
        recommendation_created_products_count=len(created_product_ids),
        picked_up_quantity_from_recommendations=total_picked_up_quantity,
        paid_amount_from_recommendations=total_paid_amount,
        average_sell_through_rate_from_recommendations=average_sell_through_rate,
        exact_accept_count=exact_accept_count,
        modified_accept_count=modified_accept_count,
        exact_accept_rate=_rate(exact_accept_count, accepted_count),
        modified_accept_rate=_rate(modified_accept_count, accepted_count),
        average_stock_delta=average_stock_delta,
        average_discount_price_delta=average_discount_price_delta,
        usage_by_recommendation_type=list(usage_type_summary.values()),
        recent_usages=recent_usages,
        recent_funnel_usages=recent_usages,
    )
