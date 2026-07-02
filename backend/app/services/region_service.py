import math

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product, ProductStatus
from app.models.store import Store
from app.models.merchant import Merchant, MerchantStatus
from app.models.user import User, UserStatus


def _apply_region_filters(statement, sido: str | None, sigungu: str | None, dong: str | None):
    if sido:
        statement = statement.where(Store.sido == sido)
    if sigungu:
        statement = statement.where(Store.sigungu == sigungu)
    if dong:
        statement = statement.where(Store.dong == dong)
    return statement


def get_region_stores(
    db: Session,
    sido: str | None = None,
    sigungu: str | None = None,
    dong: str | None = None,
) -> list[Store]:
    statement = select(Store).where(Store.is_active.is_(True))
    statement = _apply_region_filters(statement, sido, sigungu, dong)
    return list(db.scalars(statement.order_by(Store.created_at.desc())))


def get_region_products(
    db: Session,
    sido: str | None = None,
    sigungu: str | None = None,
    dong: str | None = None,
) -> list[Product]:
    statement = (
        select(Product)
        .join(Store, Product.store_id == Store.id)
        .join(Merchant, Store.merchant_id == Merchant.id)
        .join(User, Merchant.user_id == User.id)
        .where(
            Store.is_active.is_(True),
            Merchant.status == MerchantStatus.APPROVED,
            User.status == UserStatus.ACTIVE,
            User.is_active.is_(True),
            Product.status == ProductStatus.ACTIVE,
        )
    )
    statement = _apply_region_filters(statement, sido, sigungu, dong)
    return list(db.scalars(statement.order_by(Store.name.asc(), Product.created_at.desc())))


def calculate_distance_km(
    origin_latitude: float,
    origin_longitude: float,
    target_latitude: float,
    target_longitude: float,
) -> float:
    earth_radius_km = 6371.0
    origin_latitude_rad = math.radians(origin_latitude)
    target_latitude_rad = math.radians(target_latitude)
    latitude_delta = math.radians(target_latitude - origin_latitude)
    longitude_delta = math.radians(target_longitude - origin_longitude)

    haversine = (
        math.sin(latitude_delta / 2) ** 2
        + math.cos(origin_latitude_rad)
        * math.cos(target_latitude_rad)
        * math.sin(longitude_delta / 2) ** 2
    )
    central_angle = 2 * math.atan2(math.sqrt(haversine), math.sqrt(1 - haversine))
    return earth_radius_km * central_angle


def get_nearby_region_products(
    db: Session,
    latitude: float,
    longitude: float,
) -> list[tuple[Product, float]]:
    statement = (
        select(Product)
        .join(Store, Product.store_id == Store.id)
        .join(Merchant, Store.merchant_id == Merchant.id)
        .join(User, Merchant.user_id == User.id)
        .where(
            Store.is_active.is_(True),
            Merchant.status == MerchantStatus.APPROVED,
            User.status == UserStatus.ACTIVE,
            User.is_active.is_(True),
            Store.latitude.is_not(None),
            Store.longitude.is_not(None),
            Product.status == ProductStatus.ACTIVE,
        )
    )

    products_with_distance: list[tuple[Product, float]] = []
    for product in db.scalars(statement):
        store_latitude = float(product.store.latitude)
        store_longitude = float(product.store.longitude)
        distance_km = calculate_distance_km(
            latitude,
            longitude,
            store_latitude,
            store_longitude,
        )
        products_with_distance.append((product, distance_km))

    return sorted(
        products_with_distance,
        key=lambda item: (item[1], item[0].store.name, item[0].created_at),
    )
