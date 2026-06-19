from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.merchant import Merchant
from app.models.product import Product
from app.models.recommendation_action_event import RecommendationActionEvent
from app.models.store import Store
from app.schemas.recommendation_action_event import RecommendationActionEventCreate


def _ensure_owned_product(db: Session, merchant: Merchant, product_id) -> None:
    exists = db.scalar(
        select(Product.id)
        .join(Store, Product.store_id == Store.id)
        .where(Product.id == product_id, Store.merchant_id == merchant.id)
    )
    if exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")


def record_recommendation_action_event(
    db: Session,
    merchant: Merchant,
    payload: RecommendationActionEventCreate,
    commit: bool = True,
) -> RecommendationActionEvent:
    if payload.product_id is not None:
        _ensure_owned_product(db, merchant, payload.product_id)
    if payload.created_product_id is not None:
        _ensure_owned_product(db, merchant, payload.created_product_id)

    event = RecommendationActionEvent(
        merchant_id=merchant.id,
        product_id=payload.product_id,
        recommendation_type=payload.recommendation_type,
        action_priority=payload.action_priority,
        risk_label=payload.risk_label,
        event_type=payload.event_type,
        source=payload.source,
        created_product_id=payload.created_product_id,
    )
    db.add(event)
    if commit:
        db.commit()
        db.refresh(event)
    else:
        db.flush()
    return event


def get_recent_recommendation_action_events(
    db: Session,
    merchant: Merchant,
    days: int = 7,
) -> list[RecommendationActionEvent]:
    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=days)
    return list(
        db.scalars(
            select(RecommendationActionEvent)
            .where(
                RecommendationActionEvent.merchant_id == merchant.id,
                RecommendationActionEvent.created_at >= period_start,
                RecommendationActionEvent.created_at <= now,
            )
            .order_by(RecommendationActionEvent.created_at.desc())
        )
    )
