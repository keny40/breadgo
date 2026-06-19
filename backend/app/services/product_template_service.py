from datetime import date, datetime, time, timezone
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.merchant import Merchant
from app.models.product import Product
from app.models.product_template import ProductTemplate
from app.models.store import Store
from app.schemas.product import ProductDuplicateCreate
from app.schemas.product_template import (
    ProductTemplateBatchCreateRequest,
    ProductTemplateCreate,
    ProductTemplateCreateProductRequest,
    ProductTemplateUpdate,
)
from app.services.product_service import _get_owned_product, duplicate_product_for_merchant

KST = ZoneInfo("Asia/Seoul")


def _today() -> date:
    return datetime.now(KST).date()


def _combine_local(target_date: date, value: time) -> datetime:
    return datetime.combine(target_date, value, tzinfo=KST).astimezone(timezone.utc)


def _get_template(db: Session, merchant: Merchant, template_id: UUID) -> ProductTemplate:
    template = db.scalar(
        select(ProductTemplate)
        .where(
            ProductTemplate.id == template_id,
            ProductTemplate.merchant_id == merchant.id,
        )
        .options(
            selectinload(ProductTemplate.source_product),
        )
    )
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product template not found.")
    return template


def get_product_templates(db: Session, merchant: Merchant) -> list[ProductTemplate]:
    return list(
        db.scalars(
            select(ProductTemplate)
            .where(ProductTemplate.merchant_id == merchant.id)
            .options(
                selectinload(ProductTemplate.source_product).selectinload(Product.store),
            )
            .order_by(ProductTemplate.day_of_week.asc(), ProductTemplate.created_at.desc())
        )
    )


def create_product_template(db: Session, merchant: Merchant, payload: ProductTemplateCreate) -> ProductTemplate:
    _get_owned_product(db, merchant, payload.source_product_id)
    template = ProductTemplate(
        merchant_id=merchant.id,
        source_product_id=payload.source_product_id,
        template_name=payload.template_name.strip(),
        day_of_week=payload.day_of_week,
        default_stock_quantity=payload.default_stock_quantity,
        start_time=payload.start_time,
        end_time=payload.end_time,
        is_active=payload.is_active,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return _get_template(db, merchant, template.id)


def update_product_template(
    db: Session,
    merchant: Merchant,
    template_id: UUID,
    payload: ProductTemplateUpdate,
) -> ProductTemplate:
    template = _get_template(db, merchant, template_id)
    update_data = payload.model_dump(exclude_unset=True)
    if "source_product_id" in update_data:
        _get_owned_product(db, merchant, update_data["source_product_id"])

    start_time = update_data.get("start_time", template.start_time)
    end_time = update_data.get("end_time", template.end_time)
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be earlier than end_time.",
        )

    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(template, field, value)

    db.commit()
    db.refresh(template)
    return _get_template(db, merchant, template.id)


def delete_product_template(db: Session, merchant: Merchant, template_id: UUID) -> None:
    template = _get_template(db, merchant, template_id)
    db.delete(template)
    db.commit()


def create_product_from_template(
    db: Session,
    merchant: Merchant,
    template_id: UUID,
    payload: ProductTemplateCreateProductRequest,
):
    template = _get_template(db, merchant, template_id)
    target_date = payload.target_date or _today()
    duplicate_payload = ProductDuplicateCreate(
        stock_quantity=payload.stock_quantity
        if payload.stock_quantity is not None
        else template.default_stock_quantity,
        sale_starts_at=_combine_local(target_date, template.start_time),
        sale_ends_at=_combine_local(target_date, template.end_time),
        is_visible=payload.is_visible,
        name_suffix=payload.name_suffix or template.template_name,
    )
    return duplicate_product_for_merchant(db, merchant, template.source_product_id, duplicate_payload)


def create_today_products_from_templates(
    db: Session,
    merchant: Merchant,
    payload: ProductTemplateBatchCreateRequest,
):
    target_date = payload.target_date or _today()
    templates = get_product_templates(db, merchant)
    created_products = []
    skipped_template_ids = []

    for template in templates:
        if not template.is_active or template.day_of_week != target_date.weekday():
            skipped_template_ids.append(template.id)
            continue

        product = create_product_from_template(
            db,
            merchant,
            template.id,
            ProductTemplateCreateProductRequest(
                target_date=target_date,
                stock_quantity=template.default_stock_quantity,
                is_visible=payload.is_visible,
                name_suffix=payload.name_suffix or template.template_name,
            ),
        )
        created_products.append(product)

    return created_products, skipped_template_ids
