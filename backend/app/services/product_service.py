from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.merchant import Merchant
from app.models.product import Product, ProductStatus
from app.models.store import Store
from app.schemas.product import ProductCreate, ProductUpdate


def _get_owned_store(db: Session, merchant: Merchant, store_id: UUID) -> Store:
    store = db.scalar(
        select(Store).where(
            Store.id == store_id,
            Store.merchant_id == merchant.id,
        )
    )
    if store is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found.")
    return store


def _get_owned_product(db: Session, merchant: Merchant, product_id: UUID) -> Product:
    product = db.scalar(
        select(Product)
        .join(Store, Product.store_id == Store.id)
        .where(
            Product.id == product_id,
            Store.merchant_id == merchant.id,
        )
    )
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return product


def _apply_sold_out_status(product: Product) -> None:
    if product.status != ProductStatus.HIDDEN and product.quantity == 0:
        product.status = ProductStatus.SOLD_OUT


def create_product_for_store(db: Session, merchant: Merchant, payload: ProductCreate) -> Product:
    _get_owned_store(db, merchant, payload.store_id)

    product = Product(
        store_id=payload.store_id,
        name=payload.name.strip(),
        description=payload.description.strip() if payload.description else None,
        image_url=payload.image_url.strip() if payload.image_url else None,
        original_price=payload.original_price,
        discount_price=payload.discount_price,
        quantity=payload.quantity,
        allow_pickup=payload.allow_pickup,
        allow_quick_delivery=payload.allow_quick_delivery,
        allow_parcel_delivery=payload.allow_parcel_delivery,
        quick_delivery_fee=payload.quick_delivery_fee,
        parcel_delivery_fee=payload.parcel_delivery_fee,
        pickup_start_time=payload.pickup_start_time,
        pickup_end_time=payload.pickup_end_time,
        status=payload.status,
    )
    _apply_sold_out_status(product)

    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_products_by_store(db: Session, store_id: UUID) -> list[Product]:
    return list(
        db.scalars(
            select(Product)
            .where(
                Product.store_id == store_id,
                Product.status == ProductStatus.ACTIVE,
            )
            .order_by(Product.created_at.desc())
        )
    )


def get_my_products(db: Session, merchant: Merchant) -> list[Product]:
    return list(
        db.scalars(
            select(Product)
            .join(Store, Product.store_id == Store.id)
            .where(Store.merchant_id == merchant.id)
            .order_by(Product.created_at.desc())
        )
    )


def update_product(db: Session, merchant: Merchant, product_id: UUID, payload: ProductUpdate) -> Product:
    product = _get_owned_product(db, merchant, product_id)
    update_data = payload.model_dump(exclude_unset=True)

    original_price = update_data.get("original_price", product.original_price)
    discount_price = update_data.get("discount_price", product.discount_price)
    if discount_price > original_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="discount_price cannot be greater than original_price.",
        )

    pickup_start_time = update_data.get("pickup_start_time", product.pickup_start_time)
    pickup_end_time = update_data.get("pickup_end_time", product.pickup_end_time)
    if pickup_start_time >= pickup_end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="pickup_start_time must be earlier than pickup_end_time.",
        )

    allow_pickup = update_data.get("allow_pickup", product.allow_pickup)
    allow_quick_delivery = update_data.get("allow_quick_delivery", product.allow_quick_delivery)
    allow_parcel_delivery = update_data.get("allow_parcel_delivery", product.allow_parcel_delivery)
    if not (allow_pickup or allow_quick_delivery or allow_parcel_delivery):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one fulfillment method must be allowed.",
        )

    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()
            if field in {"description", "image_url"} and not value:
                value = None
        setattr(product, field, value)

    _apply_sold_out_status(product)
    db.commit()
    db.refresh(product)
    return product


def hide_product(db: Session, merchant: Merchant, product_id: UUID) -> Product:
    product = _get_owned_product(db, merchant, product_id)
    product.status = ProductStatus.HIDDEN
    db.commit()
    db.refresh(product)
    return product
