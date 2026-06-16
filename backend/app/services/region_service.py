from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product, ProductStatus
from app.models.store import Store


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
        .where(
            Store.is_active.is_(True),
            Product.status == ProductStatus.ACTIVE,
        )
    )
    statement = _apply_region_filters(statement, sido, sigungu, dong)
    return list(db.scalars(statement.order_by(Store.name.asc(), Product.created_at.desc())))
