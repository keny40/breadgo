from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.product import Product
from app.models.product_event import ProductEvent
from app.models.user import User
from app.schemas.product_event import ProductEventCreate


def record_product_event(
    db: Session,
    product_id: UUID,
    payload: ProductEventCreate,
    user: User | None = None,
    commit: bool = True,
) -> ProductEvent:
    product = db.scalar(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.store))
    )
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")

    event = ProductEvent(
        product_id=product.id,
        store_id=product.store_id,
        merchant_id=product.store.merchant_id if product.store else None,
        user_id=user.id if user else None,
        event_type=payload.event_type,
        source=payload.source,
    )
    db.add(event)
    if commit:
        db.commit()
        db.refresh(event)
    else:
        db.flush()
    return event
