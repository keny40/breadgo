from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


RecommendationActionEventType = Literal[
    "ACTION_CARD_VIEWED",
    "ACTION_CARD_CLICKED",
    "RECOMMENDATION_DETAIL_OPENED",
    "DRAFT_CREATE_STARTED",
    "DRAFT_CREATED",
]
RecommendationActionEventSource = Literal["PRO_DASHBOARD", "RECOMMENDATIONS_PAGE"]


class RecommendationActionEventCreate(BaseModel):
    product_id: UUID | None = None
    recommendation_type: str | None = None
    action_priority: str | None = None
    risk_label: str | None = None
    event_type: RecommendationActionEventType
    source: RecommendationActionEventSource
    created_product_id: UUID | None = None


class RecommendationActionEventRead(BaseModel):
    id: UUID
    merchant_id: UUID
    product_id: UUID | None
    recommendation_type: str | None
    action_priority: str | None
    risk_label: str | None
    event_type: str
    source: str
    created_product_id: UUID | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
