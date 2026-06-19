from collections import Counter, defaultdict
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
from app.models.product_event import ProductEvent
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
    reservation_count: int = 0
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


def _funnel_rate(numerator: int, denominator: int) -> float:
    return min(100.0, _rate(numerator, denominator))


def _funnel_signal(
    detail_views: int,
    reservation_started_count: int,
    reservation_count: int,
    sell_through_rate: float,
) -> tuple[str, str]:
    view_to_reservation_rate = _funnel_rate(reservation_count, detail_views)
    started_to_created_rate = _funnel_rate(reservation_count, reservation_started_count)

    if detail_views < 3:
        return (
            "INSUFFICIENT_DATA",
            "고객 반응 데이터가 아직 적습니다. 조회 데이터가 더 쌓이면 추천 정확도가 올라갑니다.",
        )
    if view_to_reservation_rate >= 50 and sell_through_rate >= 60:
        return (
            "HIGH_CONVERSION",
            "조회 대비 예약 전환이 높고 판매 흐름도 좋아 재고 확대 후보입니다.",
        )
    if reservation_started_count >= 3 and started_to_created_rate < 50:
        return (
            "HIGH_INTEREST_LOW_CONVERSION",
            "예약 의도는 있지만 최종 예약 전환이 낮습니다. 가격, 배송비, 수령 조건을 점검해 보세요.",
        )
    if detail_views >= 3 and view_to_reservation_rate < 20:
        return (
            "HIGH_INTEREST_LOW_CONVERSION",
            "조회는 많지만 예약 전환이 낮습니다. 할인가 또는 재고 운영을 조정해 볼 수 있습니다.",
        )
    if detail_views < 5 and reservation_count == 0:
        return (
            "LOW_INTEREST",
            "조회 자체가 낮아 고객 관심 데이터가 부족합니다. 노출 상품명, 이미지, 수령 시간을 점검해 보세요.",
        )
    return (
        "INSUFFICIENT_DATA",
        "고객 반응 데이터가 더 쌓이면 추천 신호를 더 명확하게 판단할 수 있습니다.",
    )


def _recommendation_explanation(
    recommendation_type: str,
    confidence_label: str,
    funnel_signal_label: str,
    sell_through_rate: float,
    pickup_completion_rate: float,
    cancellation_rate: float,
    current_stock_quantity: int,
    recommended_stock_quantity: int,
    current_discount_price: Decimal,
    recommended_discount_price: Decimal,
) -> tuple[str, list[str], list[str], str, str, str]:
    reasons: list[str] = []
    actions: list[str] = []
    risk_label = "NONE"
    action_priority = "LOW"
    title = "현재 설정을 유지하며 데이터를 더 확인하세요"
    primary_action_label = "추천값으로 초안 만들기"

    if funnel_signal_label == "HIGH_INTEREST_LOW_CONVERSION":
        title = "관심은 있지만 예약 전환이 낮습니다"
        risk_label = "LOW_CONVERSION_RISK"
        action_priority = "HIGH"
        reasons.append("상품 조회나 예약 시작은 있지만 최종 예약 생성으로 이어지는 비율이 낮습니다.")
        actions.append("할인가, 배송비, 수령 시간, 상품명/이미지를 점검하세요.")
    elif funnel_signal_label == "HIGH_CONVERSION":
        title = "고객 전환이 좋은 상품입니다"
        action_priority = "HIGH"
        reasons.append("조회 대비 예약 전환이 높아 고객 반응이 확인됩니다.")
        actions.append("재고를 소폭 늘려 추가 수요를 테스트하세요.")
    elif funnel_signal_label == "LOW_INTEREST":
        title = "고객 관심 데이터가 낮습니다"
        risk_label = "LOW_INTEREST_RISK"
        action_priority = "MEDIUM"
        reasons.append("최근 고객 조회와 예약 반응이 충분하지 않습니다.")
        actions.append("노출 상품명, 대표 이미지, 픽업 시간을 먼저 개선하세요.")
    elif funnel_signal_label == "INSUFFICIENT_DATA":
        title = "아직 판단 데이터가 부족합니다"
        risk_label = "DATA_TOO_SMALL"
        reasons.append("최근 7일 고객 반응 데이터가 충분하지 않습니다.")
        actions.append("소량으로 다시 등록해 반응 데이터를 더 쌓으세요.")

    if cancellation_rate >= 30:
        title = "예약 후 이탈이 높습니다"
        risk_label = "HIGH_CANCEL_RISK"
        action_priority = "HIGH"
        reasons.append("취소율이 높아 재고를 늘리기 전에 픽업/배송 조건 확인이 필요합니다.")
        actions.append("픽업 가능 시간과 수령 안내를 더 명확히 하세요.")

    if sell_through_rate >= 80 and pickup_completion_rate >= 80:
        reasons.append("판매율과 픽업 완료율이 높아 수요가 안정적으로 확인됩니다.")
        actions.append("추천 재고만큼 소폭 늘려 판매 기회를 확인하세요.")
        if risk_label in {"NONE", "DATA_TOO_SMALL"}:
            action_priority = "HIGH"
    elif sell_through_rate <= 30:
        reasons.append("판매율이 낮아 현재 재고가 남을 가능성이 있습니다.")
        actions.append("재고를 줄이거나 할인가를 강화해 반응을 테스트하세요.")
        if risk_label == "NONE":
            risk_label = "LOW_CONVERSION_RISK"
        if action_priority == "LOW":
            action_priority = "MEDIUM"

    if current_stock_quantity <= 1 and recommendation_type in {"INCREASE_STOCK", "RAISE_PRICE"}:
        risk_label = "LOW_STOCK_RISK"
        reasons.append("현재 남은 재고가 적어 추가 판매 기회를 놓칠 수 있습니다.")

    if recommendation_type == "INCREASE_STOCK":
        primary_action_label = "재고 늘려 초안 만들기"
        actions.insert(0, f"추천 재고 {recommended_stock_quantity}개로 초안을 만들어 보세요.")
    elif recommendation_type == "DECREASE_STOCK":
        primary_action_label = "재고 줄여 초안 만들기"
        actions.insert(0, f"추천 재고 {recommended_stock_quantity}개로 보수적으로 등록하세요.")
    elif recommendation_type == "LOWER_PRICE":
        primary_action_label = "할인가 낮춰 초안 만들기"
        actions.insert(0, f"추천 할인가 {recommended_discount_price:,.0f}원으로 가격 반응을 테스트하세요.")
    elif recommendation_type == "RAISE_PRICE":
        primary_action_label = "가격 조정 초안 만들기"
        actions.insert(0, f"추천 할인가 {recommended_discount_price:,.0f}원으로 수익성을 테스트하세요.")
    else:
        actions.insert(0, "추천값으로 소량 테스트 초안을 만들어 보세요.")

    if recommended_discount_price != current_discount_price:
        reasons.append(
            f"현재 할인가 {current_discount_price:,.0f}원에서 추천 할인가 {recommended_discount_price:,.0f}원으로 조정 후보입니다."
        )
    if confidence_label == "LOW" and action_priority == "HIGH":
        action_priority = "MEDIUM"

    unique_reasons = list(dict.fromkeys(reasons))[:4]
    unique_actions = list(dict.fromkeys(actions))[:4]
    return title, unique_reasons, unique_actions, primary_action_label, action_priority, risk_label


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
    product_ids = [product.id for product in products]
    product_events = []
    if product_ids:
        product_events = list(
            db.scalars(
                select(ProductEvent).where(
                    ProductEvent.product_id.in_(product_ids),
                    ProductEvent.created_at >= period_start,
                    ProductEvent.created_at <= now,
                )
            )
        )

    aggregates: dict[object, RecommendationAggregate] = defaultdict(RecommendationAggregate)
    for reservation in reservations:
        aggregate = aggregates[reservation.product_id]
        aggregate.reservation_count += 1
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

    detail_views = Counter(event.product_id for event in product_events if event.event_type == "DETAIL_VIEW")
    reservation_starts = Counter(
        event.product_id for event in product_events if event.event_type == "RESERVATION_STARTED"
    )

    recommendations: list[ProRecommendationRead] = []
    for product in products:
        aggregate = aggregates[product.id]
        registered_quantity = product.quantity + aggregate.reserved_quantity
        sell_through_rate = _rate(aggregate.reserved_quantity, registered_quantity)
        pickup_completion_rate = _rate(aggregate.picked_up_count, aggregate.paid_count)
        cancellation_rate = _rate(aggregate.cancelled_count, aggregate.paid_count + aggregate.cancelled_count)
        total_events = aggregate.paid_count + aggregate.cancelled_count
        confidence_label = _confidence(total_events, sell_through_rate, pickup_completion_rate, cancellation_rate)
        product_detail_views = detail_views[product.id]
        product_reservation_starts = reservation_starts[product.id]
        view_to_reservation_rate = _funnel_rate(aggregate.reservation_count, product_detail_views)
        started_to_created_rate = _funnel_rate(aggregate.reservation_count, product_reservation_starts)
        funnel_signal_label, funnel_message = _funnel_signal(
            product_detail_views,
            product_reservation_starts,
            aggregate.reservation_count,
            sell_through_rate,
        )

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

        if funnel_signal_label == "HIGH_INTEREST_LOW_CONVERSION":
            if recommendation_type not in {"DECREASE_STOCK", "LOWER_PRICE"}:
                if product.discount_price > product.original_price * Decimal("0.50"):
                    recommendation_type = "LOWER_PRICE"
                    recommended_price = _lower_price(product.discount_price)
                else:
                    recommendation_type = "DECREASE_STOCK"
                    recommended_stock = max(1, min(recommended_stock, product.quantity or recommended_stock))
            message = f"{message} {funnel_message}"
            if confidence_label == "HIGH":
                confidence_label = "MEDIUM"
        elif funnel_signal_label == "HIGH_CONVERSION":
            if recommendation_type == "KEEP":
                recommendation_type = "INCREASE_STOCK"
                recommended_stock = max(product.quantity + 1, ceil(max(base_stock, product.quantity or 1) * 1.1))
            message = f"{message} {funnel_message}"
        elif funnel_signal_label == "LOW_INTEREST":
            if aggregate.reservation_count == 0 and product.quantity > 1:
                recommendation_type = "DECREASE_STOCK"
                recommended_stock = max(1, min(recommended_stock, product.quantity))
            confidence_label = "LOW"
            message = f"{message} {funnel_message}"
        elif funnel_signal_label == "INSUFFICIENT_DATA":
            message = f"{message} {funnel_message}"

        recommended_price = _money(recommended_price)
        (
            explanation_title,
            explanation_reasons,
            suggested_actions,
            primary_action_label,
            action_priority,
            risk_label,
        ) = _recommendation_explanation(
            recommendation_type=recommendation_type,
            confidence_label=confidence_label,
            funnel_signal_label=funnel_signal_label,
            sell_through_rate=sell_through_rate,
            pickup_completion_rate=pickup_completion_rate,
            cancellation_rate=cancellation_rate,
            current_stock_quantity=product.quantity,
            recommended_stock_quantity=recommended_stock,
            current_discount_price=product.discount_price,
            recommended_discount_price=recommended_price,
        )

        recommendations.append(
            ProRecommendationRead(
                product_id=product.id,
                product_name=product.name,
                store_id=product.store_id,
                store_name=product.store.name if product.store else "매장 정보 없음",
                recent_reserved_quantity=aggregate.reserved_quantity,
                recent_picked_up_quantity=aggregate.picked_up_quantity,
                recent_cancelled_quantity=aggregate.cancelled_quantity,
                detail_views=product_detail_views,
                reservation_started_count=product_reservation_starts,
                reservation_count=aggregate.reservation_count,
                view_to_reservation_rate=view_to_reservation_rate,
                started_to_created_rate=started_to_created_rate,
                funnel_signal_label=funnel_signal_label,
                funnel_message=funnel_message,
                current_stock_quantity=product.quantity,
                sell_through_rate=sell_through_rate,
                pickup_completion_rate=pickup_completion_rate,
                recommended_stock_quantity=recommended_stock,
                current_discount_price=product.discount_price,
                recommended_discount_price=recommended_price,
                recommendation_type=recommendation_type,
                recommendation_message=message,
                confidence_label=confidence_label,
                explanation_title=explanation_title,
                explanation_reasons=explanation_reasons,
                suggested_actions=suggested_actions,
                primary_action_label=primary_action_label,
                action_priority=action_priority,
                risk_label=risk_label,
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
