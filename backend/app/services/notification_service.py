from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User, UserRole


def _role_value(user: User) -> str:
    return user.role.value.upper()


def create_notification(
    db: Session,
    user: User | None,
    title: str,
    message: str,
    notification_type: str,
    role: str | None = None,
    related_reservation_id: UUID | None = None,
    related_payment_id: UUID | None = None,
    related_settlement_id: UUID | None = None,
) -> Notification | None:
    if user is None:
        return None

    notification = Notification(
        user_id=user.id,
        role=role or _role_value(user),
        title=title,
        message=message,
        notification_type=notification_type,
        related_reservation_id=related_reservation_id,
        related_payment_id=related_payment_id,
        related_settlement_id=related_settlement_id,
    )
    db.add(notification)
    return notification


def create_admin_notifications(
    db: Session,
    title: str,
    message: str,
    notification_type: str,
    related_reservation_id: UUID | None = None,
    related_payment_id: UUID | None = None,
    related_settlement_id: UUID | None = None,
) -> None:
    admins = list(db.scalars(select(User).where(User.role == UserRole.ADMIN)))
    for admin in admins:
        create_notification(
            db,
            user=admin,
            role="ADMIN",
            title=title,
            message=message,
            notification_type=notification_type,
            related_reservation_id=related_reservation_id,
            related_payment_id=related_payment_id,
            related_settlement_id=related_settlement_id,
        )


def list_my_notifications(db: Session, user: User) -> list[Notification]:
    return list(
        db.scalars(
            select(Notification)
            .where(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
        )
    )


def mark_as_read(db: Session, user: User, notification_id: UUID) -> Notification:
    notification = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user.id,
        )
    )
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    notification.is_read = True
    notification.read_at = notification.read_at or datetime.now(timezone.utc)
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_as_read(db: Session, user: User) -> list[Notification]:
    notifications = list(db.scalars(select(Notification).where(Notification.user_id == user.id)))
    now = datetime.now(timezone.utc)
    for notification in notifications:
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = now
    db.commit()
    return list_my_notifications(db, user)
