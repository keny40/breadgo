from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.inventory_alert_action import InventoryAlertAction
from app.models.merchant import Merchant
from app.models.product import Product
from app.models.store import Store
from app.schemas.inventory_alert_action import InventoryAlertActionCreate, InventoryAlertActionRead

ALERT_ACTION_TYPES = {"ACKNOWLEDGED", "ACTION_STARTED", "MARKED_RESOLVED", "DISMISSED"}
ALERT_SEVERITIES = {"HIGH", "MEDIUM", "LOW"}


def _validate_owned_product(db: Session, merchant: Merchant, product_id: UUID) -> Product:
    product = db.scalar(
        select(Product)
        .join(Store, Product.store_id == Store.id)
        .where(Product.id == product_id, Store.merchant_id == merchant.id)
    )
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return product


def _to_read(action: InventoryAlertAction) -> InventoryAlertActionRead:
    return InventoryAlertActionRead(
        id=action.id,
        merchant_id=action.merchant_id,
        product_id=action.product_id,
        product_name=action.product.name if action.product else None,
        alert_type=action.alert_type,
        severity=action.severity,
        action_type=action.action_type,
        note=action.note,
        created_at=action.created_at,
    )


def create_inventory_alert_action(
    db: Session,
    merchant: Merchant,
    payload: InventoryAlertActionCreate,
) -> InventoryAlertActionRead:
    action_type = payload.action_type.strip().upper()
    if action_type not in ALERT_ACTION_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="action_type must be ACKNOWLEDGED, ACTION_STARTED, MARKED_RESOLVED, or DISMISSED.",
        )
    severity = payload.severity.strip().upper()
    if severity not in ALERT_SEVERITIES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="severity must be HIGH, MEDIUM, or LOW.")

    if payload.product_id is not None:
        _validate_owned_product(db, merchant, payload.product_id)

    action = InventoryAlertAction(
        merchant_id=merchant.id,
        product_id=payload.product_id,
        alert_type=payload.alert_type.strip().upper(),
        severity=severity,
        action_type=action_type,
        note=payload.note.strip() if payload.note else None,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return _to_read(action)


def list_inventory_alert_actions(
    db: Session,
    merchant: Merchant,
    *,
    product_id: UUID | None = None,
    alert_type: str | None = None,
    limit: int = 50,
) -> list[InventoryAlertActionRead]:
    query = (
        select(InventoryAlertAction)
        .options(selectinload(InventoryAlertAction.product))
        .where(InventoryAlertAction.merchant_id == merchant.id)
        .order_by(InventoryAlertAction.created_at.desc())
        .limit(min(max(limit, 1), 100))
    )
    if product_id is not None:
        query = query.where(InventoryAlertAction.product_id == product_id)
    if alert_type:
        query = query.where(InventoryAlertAction.alert_type == alert_type.strip().upper())
    return [_to_read(action) for action in db.scalars(query).all()]


def latest_inventory_alert_actions_by_key(
    db: Session,
    merchant: Merchant,
) -> dict[tuple[UUID | None, str], InventoryAlertAction]:
    actions = db.scalars(
        select(InventoryAlertAction)
        .where(InventoryAlertAction.merchant_id == merchant.id)
        .order_by(InventoryAlertAction.created_at.desc())
    ).all()
    latest: dict[tuple[UUID | None, str], InventoryAlertAction] = {}
    for action in actions:
        key = (action.product_id, action.alert_type)
        if key not in latest:
            latest[key] = action
    return latest
