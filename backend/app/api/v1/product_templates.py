from uuid import UUID

from fastapi import APIRouter, Body, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.product_template import ProductTemplate
from app.models.user import User
from app.schemas.product import ProductRead
from app.schemas.product_template import (
    ProductTemplateBatchCreateRequest,
    ProductTemplateCreate,
    ProductTemplateCreateProductRequest,
    ProductTemplateCreateProductsResponse,
    ProductTemplateRead,
    ProductTemplateUpdate,
)
from app.services.merchant_service import require_merchant_for_user
from app.services.product_template_service import (
    create_product_from_template,
    create_product_template,
    create_today_products_from_templates,
    delete_product_template,
    get_product_templates,
    update_product_template,
)

router = APIRouter()


def template_to_read(template: ProductTemplate) -> ProductTemplateRead:
    payload = ProductTemplateRead.model_validate(template)
    if template.source_product:
        payload.source_product_name = template.source_product.name
        payload.source_store_name = template.source_product.store.name if template.source_product.store else None
    return payload


@router.get("", response_model=list[ProductTemplateRead])
def list_product_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProductTemplateRead]:
    merchant = require_merchant_for_user(db, current_user)
    return [template_to_read(template) for template in get_product_templates(db, merchant)]


@router.post("", response_model=ProductTemplateRead, status_code=status.HTTP_201_CREATED)
def create_template(
    payload: ProductTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProductTemplateRead:
    merchant = require_merchant_for_user(db, current_user)
    return template_to_read(create_product_template(db, merchant, payload))


@router.patch("/{template_id}", response_model=ProductTemplateRead)
def update_template(
    template_id: UUID,
    payload: ProductTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProductTemplateRead:
    merchant = require_merchant_for_user(db, current_user)
    return template_to_read(update_product_template(db, merchant, template_id, payload))


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    merchant = require_merchant_for_user(db, current_user)
    delete_product_template(db, merchant, template_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{template_id}/create-product", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    template_id: UUID,
    payload: ProductTemplateCreateProductRequest = Body(default_factory=ProductTemplateCreateProductRequest),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProductRead:
    merchant = require_merchant_for_user(db, current_user)
    product = create_product_from_template(db, merchant, template_id, payload)
    return ProductRead.model_validate(product)


@router.post("/create-today-products", response_model=ProductTemplateCreateProductsResponse)
def create_today_products(
    payload: ProductTemplateBatchCreateRequest = Body(default_factory=ProductTemplateBatchCreateRequest),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProductTemplateCreateProductsResponse:
    merchant = require_merchant_for_user(db, current_user)
    products, skipped_template_ids = create_today_products_from_templates(db, merchant, payload)
    return ProductTemplateCreateProductsResponse(
        created_products=[ProductRead.model_validate(product) for product in products],
        skipped_template_ids=skipped_template_ids,
    )

