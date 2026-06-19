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
from app.models.settlement import SettlementStatus
from app.models.store import Store
from app.schemas.pro_dashboard import MerchantProDashboardRead, ProDailySummary, ProProductSummary

KST = ZoneInfo("Asia/Seoul")
ZERO = Decimal("0.00")


@dataclass
class ProductAggregate:
    product: Product
    store_name: str
    reserved_quantity: int = 0
    paid_quantity: int = 0
    picked_up_quantity: int = 0
    cancelled_quantity: int = 0
    paid_count: int = 0
    picked_up_count: int = 0
    cancelled_count: int = 0
    gross_sales: Decimal = ZERO
    estimated_settlement: Decimal = ZERO
    saved_amount: Decimal = ZERO


def _day_window(target_date: date) -> tuple[datetime, datetime]:
    start = datetime.combine(target_date, time.min, tzinfo=KST)
    end = start + timedelta(days=1)
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def _today() -> date:
    return datetime.now(KST).date()


def _rate(numerator: int | Decimal, denominator: int | Decimal) -> float:
    if denominator == 0:
        return 0.0
    return round(float(numerator) / float(denominator) * 100, 1)


def _is_in_kst_day(value: datetime, target_date: date) -> bool:
    return value.astimezone(KST).date() == target_date


def build_merchant_pro_dashboard(db: Session, merchant: Merchant) -> MerchantProDashboardRead:
    today = _today()
    recent_dates = [today - timedelta(days=offset) for offset in range(6, -1, -1)]
    recent_start, _ = _day_window(recent_dates[0])
    _, today_end = _day_window(today)

    products = list(
        db.scalars(
            select(Product)
            .join(Store, Product.store_id == Store.id)
            .where(Store.merchant_id == merchant.id)
            .options(selectinload(Product.store))
            .order_by(Product.pickup_start_time.desc(), Product.created_at.desc())
        )
    )

    reservations = list(
        db.scalars(
            select(Reservation)
            .join(Store, Reservation.store_id == Store.id)
            .where(
                Store.merchant_id == merchant.id,
                Reservation.created_at >= recent_start,
                Reservation.created_at < today_end,
            )
            .options(
                selectinload(Reservation.product),
                selectinload(Reservation.store),
                selectinload(Reservation.payment),
                selectinload(Reservation.settlement),
            )
        )
    )

    reservations_by_product: dict[object, list[Reservation]] = defaultdict(list)
    for reservation in reservations:
        reservations_by_product[reservation.product_id].append(reservation)

    today_product_ids = {
        product.id
        for product in products
        if _is_in_kst_day(product.pickup_start_time, today) or _is_in_kst_day(product.pickup_end_time, today)
    }
    today_product_ids.update(
        reservation.product_id
        for reservation in reservations
        if _is_in_kst_day(reservation.created_at, today)
    )

    product_summaries: list[ProProductSummary] = []
    totals_registered = 0
    totals_reserved = 0
    totals_paid_count = 0
    totals_picked_up_count = 0
    totals_cancelled_count = 0
    totals_remaining = 0
    totals_gross = ZERO
    totals_settlement = ZERO
    totals_saved_items = 0
    totals_saved_amount = ZERO

    for product in products:
        if product.id not in today_product_ids:
            continue

        aggregate = ProductAggregate(
            product=product,
            store_name=product.store.name if product.store else "매장 정보 없음",
        )
        today_reservations = [
            reservation
            for reservation in reservations_by_product.get(product.id, [])
            if _is_in_kst_day(reservation.created_at, today)
        ]

        for reservation in today_reservations:
            if reservation.status != ReservationStatus.CANCELLED:
                aggregate.reserved_quantity += reservation.quantity

            if reservation.payment and reservation.payment.status == PaymentStatus.PAID:
                aggregate.paid_quantity += reservation.quantity
                aggregate.paid_count += 1
                aggregate.gross_sales += reservation.product_amount
                if reservation.settlement and reservation.settlement.status != SettlementStatus.CANCELLED:
                    aggregate.estimated_settlement += reservation.settlement.merchant_settlement_amount

            if reservation.status == ReservationStatus.PICKED_UP:
                aggregate.picked_up_quantity += reservation.quantity
                aggregate.picked_up_count += 1
                aggregate.saved_amount += reservation.product_amount

            if reservation.status == ReservationStatus.CANCELLED:
                aggregate.cancelled_quantity += reservation.quantity
                aggregate.cancelled_count += 1

        registered_quantity = product.quantity + aggregate.reserved_quantity
        remaining_quantity = product.quantity
        sell_through_rate = _rate(aggregate.reserved_quantity, registered_quantity)

        totals_registered += registered_quantity
        totals_reserved += aggregate.reserved_quantity
        totals_paid_count += aggregate.paid_count
        totals_picked_up_count += aggregate.picked_up_count
        totals_cancelled_count += aggregate.cancelled_count
        totals_remaining += remaining_quantity
        totals_gross += aggregate.gross_sales
        totals_settlement += aggregate.estimated_settlement
        totals_saved_items += aggregate.picked_up_quantity
        totals_saved_amount += aggregate.saved_amount

        product_summaries.append(
            ProProductSummary(
                product_id=product.id,
                product_name=product.name,
                store_id=product.store_id,
                store_name=aggregate.store_name,
                status=product.status.value,
                registered_quantity=registered_quantity,
                reserved_quantity=aggregate.reserved_quantity,
                paid_quantity=aggregate.paid_quantity,
                picked_up_quantity=aggregate.picked_up_quantity,
                cancelled_quantity=aggregate.cancelled_quantity,
                remaining_quantity=remaining_quantity,
                gross_sales=aggregate.gross_sales,
                estimated_settlement=aggregate.estimated_settlement,
                sell_through_rate=sell_through_rate,
            )
        )

    recent_7_days = _build_recent_7_days(products, reservations, recent_dates)

    return MerchantProDashboardRead(
        merchant_id=merchant.id,
        business_name=merchant.business_name,
        today_registered_quantity=totals_registered,
        today_reserved_quantity=totals_reserved,
        today_paid_count=totals_paid_count,
        today_picked_up_count=totals_picked_up_count,
        today_cancelled_count=totals_cancelled_count,
        today_remaining_quantity=totals_remaining,
        today_gross_sales=totals_gross,
        today_estimated_settlement=totals_settlement,
        today_estimated_saved_items=totals_saved_items,
        today_estimated_waste_prevented_amount=totals_saved_amount,
        sell_through_rate=_rate(totals_reserved, totals_registered),
        pickup_completion_rate=_rate(totals_picked_up_count, totals_paid_count),
        cancellation_rate=_rate(totals_cancelled_count, totals_paid_count + totals_cancelled_count),
        product_summaries=sorted(product_summaries, key=lambda item: item.sell_through_rate, reverse=True),
        recent_7_days=recent_7_days,
    )


def _build_recent_7_days(
    products: list[Product],
    reservations: list[Reservation],
    recent_dates: list[date],
) -> list[ProDailySummary]:
    products_by_date: dict[date, list[Product]] = defaultdict(list)
    for product in products:
        product_day = product.pickup_start_time.astimezone(KST).date()
        if product_day in recent_dates:
            products_by_date[product_day].append(product)

    reservations_by_date: dict[date, list[Reservation]] = defaultdict(list)
    for reservation in reservations:
        reservations_by_date[reservation.created_at.astimezone(KST).date()].append(reservation)

    summaries: list[ProDailySummary] = []
    for target_date in recent_dates:
        day_products = {product.id: product for product in products_by_date.get(target_date, [])}
        day_reservations = reservations_by_date.get(target_date, [])
        for reservation in day_reservations:
            if reservation.product:
                day_products[reservation.product_id] = reservation.product

        reserved_quantity = sum(
            reservation.quantity
            for reservation in day_reservations
            if reservation.status != ReservationStatus.CANCELLED
        )
        picked_up_quantity = sum(
            reservation.quantity
            for reservation in day_reservations
            if reservation.status == ReservationStatus.PICKED_UP
        )
        cancelled_count = sum(1 for reservation in day_reservations if reservation.status == ReservationStatus.CANCELLED)
        gross_sales = sum(
            (
                reservation.product_amount
                for reservation in day_reservations
                if reservation.payment and reservation.payment.status == PaymentStatus.PAID
            ),
            ZERO,
        )
        estimated_settlement = sum(
            (
                reservation.settlement.merchant_settlement_amount
                for reservation in day_reservations
                if reservation.settlement and reservation.settlement.status != SettlementStatus.CANCELLED
            ),
            ZERO,
        )
        remaining_quantity = sum(product.quantity for product in day_products.values())
        registered_quantity = remaining_quantity + reserved_quantity

        summaries.append(
            ProDailySummary(
                date=target_date,
                registered_quantity=registered_quantity,
                reserved_quantity=reserved_quantity,
                picked_up_quantity=picked_up_quantity,
                cancelled_count=cancelled_count,
                remaining_quantity=remaining_quantity,
                gross_sales=gross_sales,
                estimated_settlement=estimated_settlement,
                sell_through_rate=_rate(reserved_quantity, registered_quantity),
            )
        )

    return summaries

