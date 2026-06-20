from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.merchant import Merchant
from app.models.product import Product
from app.models.product_inventory_event import ProductInventoryEvent
from app.models.store import Store
from app.schemas.product_inventory_event import ProductInventoryEventRead


def record_inventory_event(
    db: Session,
    *,
    merchant_id: UUID,
    store_id: UUID | None,
    product_id: UUID,
    event_type: str,
    quantity_before: int | None,
    quantity_after: int | None,
    source_type: str | None = None,
    source_id: UUID | None = None,
    note: str | None = None,
    commit: bool = False,
) -> ProductInventoryEvent:
    quantity_delta = None
    if quantity_before is not None and quantity_after is not None:
        quantity_delta = quantity_after - quantity_before

    event = ProductInventoryEvent(
        merchant_id=merchant_id,
        store_id=store_id,
        product_id=product_id,
        event_type=event_type,
        quantity_before=quantity_before,
        quantity_after=quantity_after,
        quantity_delta=quantity_delta,
        source_type=source_type,
        source_id=source_id,
        note=note,
    )
    db.add(event)
    if commit:
        db.commit()
        db.refresh(event)
    return event


def _to_read(event: ProductInventoryEvent) -> ProductInventoryEventRead:
    return ProductInventoryEventRead(
        id=event.id,
        merchant_id=event.merchant_id,
        store_id=event.store_id,
        product_id=event.product_id,
        product_name=event.product.name if event.product else None,
        store_name=event.store.name if event.store else None,
        event_type=event.event_type,
        quantity_before=event.quantity_before,
        quantity_after=event.quantity_after,
        quantity_delta=event.quantity_delta,
        source_type=event.source_type,
        source_id=event.source_id,
        note=event.note,
        created_at=event.created_at,
    )


def list_inventory_events(
    db: Session,
    merchant: Merchant,
    *,
    product_id: UUID | None = None,
    event_type: str | None = None,
    source_type: str | None = None,
    limit: int = 50,
) -> list[ProductInventoryEventRead]:
    query = (
        select(ProductInventoryEvent)
        .options(
            selectinload(ProductInventoryEvent.product),
            selectinload(ProductInventoryEvent.store),
        )
        .where(ProductInventoryEvent.merchant_id == merchant.id)
        .order_by(ProductInventoryEvent.created_at.desc())
        .limit(min(max(limit, 1), 100))
    )
    if product_id is not None:
        query = query.where(ProductInventoryEvent.product_id == product_id)
    if event_type:
        query = query.where(ProductInventoryEvent.event_type == event_type)
    if source_type:
        query = query.where(ProductInventoryEvent.source_type == source_type)

    return [_to_read(event) for event in db.scalars(query).all()]


def list_product_inventory_events(
    db: Session,
    merchant: Merchant,
    product_id: UUID,
    *,
    limit: int = 50,
) -> list[ProductInventoryEventRead]:
    product = db.scalar(
        select(Product)
        .join(Store, Product.store_id == Store.id)
        .where(Product.id == product_id, Store.merchant_id == merchant.id)
    )
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return list_inventory_events(db, merchant, product_id=product_id, limit=limit)
