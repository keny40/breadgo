from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.merchant import Merchant
from app.models.payment import PaymentStatus
from app.models.product import Product
from app.models.reservation import Reservation, ReservationStatus
from app.models.store import Store
from app.schemas.pro_esg import MerchantProEsgReportRead, ProEsgDailyTrend, ProEsgProductSummary

KST = ZoneInfo("Asia/Seoul")
ZERO = Decimal("0.00")


@dataclass
class EsgProductAggregate:
    product_id: object
    product_name: str
    store_id: object
    store_name: str
    saved_items: int = 0
    saved_amount: Decimal = ZERO
    pickup_completed_count: int = 0
    cancelled_count: int = 0


def _today() -> date:
    return datetime.now(KST).date()


def _day_window(target_date: date) -> tuple[datetime, datetime]:
    start = datetime.combine(target_date, time.min, tzinfo=KST)
    end = start + timedelta(days=1)
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def _month_start(target_date: date) -> date:
    return target_date.replace(day=1)


def _as_kst_date(value: datetime) -> date:
    return value.astimezone(KST).date()


def _rate(numerator: int | Decimal, denominator: int | Decimal) -> float:
    if denominator == 0:
        return 0.0
    return round(float(numerator) / float(denominator) * 100, 1)


def _is_completed_pickup(reservation: Reservation) -> bool:
    return (
        reservation.status == ReservationStatus.PICKED_UP
        and reservation.payment is not None
        and reservation.payment.status == PaymentStatus.PAID
    )


def build_merchant_pro_esg_report(db: Session, merchant: Merchant) -> MerchantProEsgReportRead:
    today = _today()
    week_dates = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    month_start_date = _month_start(today)
    month_start, _ = _day_window(month_start_date)
    _, today_end = _day_window(today)

    products = list(
        db.scalars(
            select(Product)
            .join(Store, Product.store_id == Store.id)
            .where(Store.merchant_id == merchant.id)
            .options(selectinload(Product.store))
        )
    )

    reservations = list(
        db.scalars(
            select(Reservation)
            .join(Store, Reservation.store_id == Store.id)
            .where(
                Store.merchant_id == merchant.id,
                Reservation.created_at >= month_start,
                Reservation.created_at < today_end,
            )
            .options(
                selectinload(Reservation.product),
                selectinload(Reservation.store),
                selectinload(Reservation.payment),
            )
        )
    )

    today_saved_items = 0
    week_saved_items = 0
    month_saved_items = 0
    today_saved_amount = ZERO
    week_saved_amount = ZERO
    month_saved_amount = ZERO
    pickup_completed_count = 0
    cancelled_count = 0
    reserved_quantity = 0
    product_aggregates: dict[object, EsgProductAggregate] = {}
    daily_saved_items: dict[date, int] = defaultdict(int)
    daily_saved_amount: dict[date, Decimal] = defaultdict(lambda: ZERO)
    daily_pickup_count: dict[date, int] = defaultdict(int)
    daily_cancelled_count: dict[date, int] = defaultdict(int)

    for reservation in reservations:
        if reservation.status != ReservationStatus.CANCELLED:
            reserved_quantity += reservation.quantity

        event_date = _as_kst_date(reservation.updated_at)
        if reservation.status == ReservationStatus.CANCELLED:
            cancelled_count += 1
            if event_date in week_dates:
                daily_cancelled_count[event_date] += 1
            continue

        if not _is_completed_pickup(reservation):
            continue

        saved_items = reservation.quantity
        saved_amount = reservation.product_amount
        month_saved_items += saved_items
        month_saved_amount += saved_amount
        pickup_completed_count += 1

        if event_date == today:
            today_saved_items += saved_items
            today_saved_amount += saved_amount
        if event_date in week_dates:
            week_saved_items += saved_items
            week_saved_amount += saved_amount
            daily_saved_items[event_date] += saved_items
            daily_saved_amount[event_date] += saved_amount
            daily_pickup_count[event_date] += 1

        product_name = reservation.product.name if reservation.product else "상품 정보 없음"
        store_name = reservation.store.name if reservation.store else "매장 정보 없음"
        aggregate = product_aggregates.setdefault(
            reservation.product_id,
            EsgProductAggregate(
                product_id=reservation.product_id,
                product_name=product_name,
                store_id=reservation.store_id,
                store_name=store_name,
            ),
        )
        aggregate.saved_items += saved_items
        aggregate.saved_amount += saved_amount
        aggregate.pickup_completed_count += 1

    for reservation in reservations:
        if reservation.status != ReservationStatus.CANCELLED:
            continue
        aggregate = product_aggregates.get(reservation.product_id)
        if aggregate is not None:
            aggregate.cancelled_count += 1

    remaining_quantity = sum(product.quantity for product in products)
    registered_quantity = remaining_quantity + reserved_quantity
    product_summaries = [
        ProEsgProductSummary(
            product_id=aggregate.product_id,
            product_name=aggregate.product_name,
            store_id=aggregate.store_id,
            store_name=aggregate.store_name,
            saved_items=aggregate.saved_items,
            saved_amount=aggregate.saved_amount,
            pickup_completed_count=aggregate.pickup_completed_count,
            cancelled_count=aggregate.cancelled_count,
            contribution_rate=_rate(aggregate.saved_items, month_saved_items),
        )
        for aggregate in product_aggregates.values()
    ]

    return MerchantProEsgReportRead(
        merchant_id=merchant.id,
        business_name=merchant.business_name,
        today_saved_items=today_saved_items,
        week_saved_items=week_saved_items,
        month_saved_items=month_saved_items,
        today_saved_amount=today_saved_amount,
        week_saved_amount=week_saved_amount,
        month_saved_amount=month_saved_amount,
        estimated_waste_reduction_items=month_saved_items,
        estimated_waste_prevention_amount=month_saved_amount,
        pickup_completed_count=pickup_completed_count,
        cancelled_count=cancelled_count,
        sell_through_rate=_rate(reserved_quantity, registered_quantity),
        carbon_reduction_note="실제 중량과 품목별 배출계수 데이터가 없어 탄소 절감량은 추정 준비 중입니다.",
        product_esg_summaries=sorted(product_summaries, key=lambda item: item.saved_items, reverse=True),
        daily_esg_trend=[
            ProEsgDailyTrend(
                date=target_date,
                saved_items=daily_saved_items[target_date],
                saved_amount=daily_saved_amount[target_date],
                pickup_completed_count=daily_pickup_count[target_date],
                cancelled_count=daily_cancelled_count[target_date],
            )
            for target_date in week_dates
        ],
    )

