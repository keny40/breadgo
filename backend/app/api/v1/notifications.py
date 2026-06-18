from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import NotificationRead
from app.services.notification_service import list_my_notifications, mark_all_as_read, mark_as_read


router = APIRouter()


@router.get("/me", response_model=list[NotificationRead])
def get_my_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NotificationRead]:
    return [NotificationRead.model_validate(item) for item in list_my_notifications(db, current_user)]


@router.patch("/{notification_id}/read", response_model=NotificationRead)
def read_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationRead:
    return NotificationRead.model_validate(mark_as_read(db, current_user, notification_id))


@router.patch("/read-all", response_model=list[NotificationRead])
def read_all_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NotificationRead]:
    return [NotificationRead.model_validate(item) for item in mark_all_as_read(db, current_user)]
