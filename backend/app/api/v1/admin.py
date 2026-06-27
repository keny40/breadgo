from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import AdminSummary, DemoSeedResponse, MerchantStatusUpdate
from app.schemas.auth import UserResponse
from app.schemas.merchant import MerchantRead
from app.schemas.payment import PaymentRead
from app.schemas.pro_daily_brief import (
    AdminProWeeklyReportBatchRunMonitorRead,
    AdminProWeeklyReportDeliveryRunHistoryRead,
    AdminWeeklyReportBatchPreviewRead,
    ProWeeklyReportDeliveryRunRead,
    ProWeeklyReportBatchRunRead,
)
from app.schemas.product import ProductRead
from app.schemas.reservation import DeliveryStatusUpdate, ReservationRead
from app.schemas.reservation_history import ReservationHistoryRead
from app.schemas.store import StoreRead
from app.services.admin_service import (
    get_admin_summary,
    get_merchants,
    get_payments,
    get_products,
    get_reservations,
    get_stores,
    get_users,
    require_admin_user,
    update_merchant_status,
)
from app.services.reservation_service import update_delivery_status_for_admin
from app.services.reservation_history_service import get_history_for_admin
from app.services.pro_daily_brief_service import (
    create_admin_weekly_report_batch_run,
    create_weekly_report_delivery_preview,
    get_admin_weekly_report_batch_run,
    get_weekly_report_delivery_run,
    list_weekly_report_delivery_runs,
    list_admin_weekly_report_batch_runs,
    preview_admin_weekly_report_batch_run,
    retry_failed_weekly_report_batch_items,
)
from app.api.v1.reservations import reservation_history_to_read, reservation_to_read
from scripts.seed_demo import seed_demo_data


router = APIRouter()


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    return require_admin_user(current_user)


@router.get("/summary", response_model=AdminSummary)
def get_summary(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminSummary:
    return get_admin_summary(db)


@router.get("/users", response_model=list[UserResponse])
def list_users(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    return [UserResponse.model_validate(user) for user in get_users(db)]


@router.get("/merchants", response_model=list[MerchantRead])
def list_merchants(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[MerchantRead]:
    return [MerchantRead.model_validate(merchant) for merchant in get_merchants(db)]


@router.get("/stores", response_model=list[StoreRead])
def list_stores(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[StoreRead]:
    return [StoreRead.model_validate(store) for store in get_stores(db)]


@router.get("/products", response_model=list[ProductRead])
def list_products(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[ProductRead]:
    return [ProductRead.model_validate(product) for product in get_products(db)]


@router.get("/reservations", response_model=list[ReservationRead])
def list_reservations(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[ReservationRead]:
    return [ReservationRead.model_validate(reservation) for reservation in get_reservations(db)]


@router.patch("/reservations/{reservation_id}/delivery-status", response_model=ReservationRead)
def change_reservation_delivery_status(
    reservation_id: UUID,
    payload: DeliveryStatusUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ReservationRead:
    reservation = update_delivery_status_for_admin(db, reservation_id, payload, current_admin)
    return reservation_to_read(reservation)


@router.get("/reservations/{reservation_id}/history", response_model=list[ReservationHistoryRead])
def get_admin_reservation_history(
    reservation_id: UUID,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[ReservationHistoryRead]:
    events = get_history_for_admin(db, reservation_id)
    return [reservation_history_to_read(event) for event in events]


@router.get("/payments", response_model=list[PaymentRead])
def list_payments(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> list[PaymentRead]:
    return [PaymentRead.model_validate(payment) for payment in get_payments(db)]


@router.patch("/merchants/{merchant_id}/status", response_model=MerchantRead)
def change_merchant_status(
    merchant_id: UUID,
    payload: MerchantStatusUpdate,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> MerchantRead:
    merchant = update_merchant_status(db, merchant_id, payload)
    return MerchantRead.model_validate(merchant)


@router.post("/demo/seed", response_model=DemoSeedResponse)
def seed_demo(
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> DemoSeedResponse:
    return DemoSeedResponse(**seed_demo_data(db))


@router.post("/pro/weekly-report/delivery-runs/preview", response_model=ProWeeklyReportDeliveryRunRead)
def create_weekly_report_delivery_preview_for_admin(
    start_date: date | None = None,
    end_date: date | None = None,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProWeeklyReportDeliveryRunRead:
    return create_weekly_report_delivery_preview(db, start_date=start_date, end_date=end_date)


@router.get("/pro/weekly-report/delivery-runs", response_model=AdminProWeeklyReportDeliveryRunHistoryRead)
def list_weekly_report_delivery_runs_for_admin(
    limit: int = 50,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminProWeeklyReportDeliveryRunHistoryRead:
    return list_weekly_report_delivery_runs(db, limit=limit)


@router.get("/pro/weekly-report/delivery-runs/{delivery_run_id}", response_model=ProWeeklyReportDeliveryRunRead)
def get_weekly_report_delivery_run_for_admin(
    delivery_run_id: UUID,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProWeeklyReportDeliveryRunRead:
    return get_weekly_report_delivery_run(db, delivery_run_id)


@router.get("/pro/weekly-report/batch-runs", response_model=AdminProWeeklyReportBatchRunMonitorRead)
def list_weekly_report_batch_runs_for_admin(
    status_filter: str | None = Query(default=None, alias="status"),
    run_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 50,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminProWeeklyReportBatchRunMonitorRead:
    return list_admin_weekly_report_batch_runs(
        db,
        status_filter=status_filter,
        run_type=run_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )


@router.post("/pro/weekly-report/batch-runs/preview", response_model=AdminWeeklyReportBatchPreviewRead)
def preview_weekly_report_batch_run_for_admin(
    start_date: date | None = None,
    end_date: date | None = None,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> AdminWeeklyReportBatchPreviewRead:
    return preview_admin_weekly_report_batch_run(db, start_date=start_date, end_date=end_date)


@router.post("/pro/weekly-report/batch-runs", response_model=ProWeeklyReportBatchRunRead)
def create_weekly_report_batch_run_for_admin(
    start_date: date | None = None,
    end_date: date | None = None,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProWeeklyReportBatchRunRead:
    return create_admin_weekly_report_batch_run(db, start_date=start_date, end_date=end_date)


@router.post("/pro/weekly-report/batch-runs/{batch_run_id}/retry-failed", response_model=ProWeeklyReportBatchRunRead)
def retry_failed_weekly_report_batch_items_for_admin(
    batch_run_id: UUID,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProWeeklyReportBatchRunRead:
    return retry_failed_weekly_report_batch_items(db, batch_run_id)


@router.get("/pro/weekly-report/batch-runs/{batch_run_id}", response_model=ProWeeklyReportBatchRunRead)
def get_weekly_report_batch_run_for_admin(
    batch_run_id: UUID,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ProWeeklyReportBatchRunRead:
    return get_admin_weekly_report_batch_run(db, batch_run_id)
