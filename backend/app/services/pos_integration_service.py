from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.merchant import Merchant
from app.models.pos_integration import PosIntegration, PosSyncBatch, PosSyncRow
from app.models.product import ProductStatus
from app.models.store import Store
from app.schemas.pos_integration import (
    MockPosSyncRequest,
    MockPosSyncResult,
    PosIntegrationRead,
    PosIntegrationUpsert,
    PosSyncBatchRead,
)
from app.schemas.product import ProductCreate
from app.services.pos_providers.base import NormalizedPosItem
from app.services.pos_providers.generic import GenericPosProvider
from app.services.pos_providers.mock import MockPosProvider
from app.services.product_service import (
    _apply_import_update,
    _find_duplicate_product,
    _get_owned_store,
    _product_has_reservations,
    create_product_for_store,
)

POS_PROVIDERS = {"MOCK_POS", "GENERIC_POS"}
POS_UPDATE_MODES = {"UPDATE_HIDDEN_ONLY", "UPDATE_IF_NO_RESERVATIONS", "SKIP_EXISTING"}
POS_DEFAULT_PRODUCT_STATUSES = {"HIDDEN"}


def _validate_provider(provider: str) -> str:
    normalized = provider.strip().upper()
    if normalized not in POS_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="provider must be MOCK_POS or GENERIC_POS.",
        )
    return normalized


def _get_default_store(db: Session, merchant: Merchant) -> Store:
    store = db.scalar(select(Store).where(Store.merchant_id == merchant.id).order_by(Store.created_at.asc()))
    if store is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="POS sync requires a registered store.")
    return store


def get_or_create_pos_integration(db: Session, merchant: Merchant) -> PosIntegration:
    integration = db.scalar(
        select(PosIntegration)
        .where(PosIntegration.merchant_id == merchant.id)
        .order_by(PosIntegration.created_at.asc())
        .limit(1)
    )
    if integration is not None:
        return integration

    integration = PosIntegration(
        merchant_id=merchant.id,
        store_id=None,
        provider="MOCK_POS",
        status="DISCONNECTED",
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration


def upsert_pos_integration(db: Session, merchant: Merchant, payload: PosIntegrationUpsert) -> PosIntegration:
    provider = _validate_provider(payload.provider)
    store_id = payload.store_id
    if store_id is not None:
        _get_owned_store(db, merchant, store_id)

    integration = get_or_create_pos_integration(db, merchant)
    integration.provider = provider
    integration.store_id = store_id
    integration.external_store_code = payload.external_store_code.strip() if payload.external_store_code else None
    integration.status = "CONNECTED"
    integration.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(integration)
    return integration


def _normalize_sync_policy(payload: MockPosSyncRequest) -> tuple[str, ProductStatus]:
    update_mode = payload.update_mode.strip().upper()
    if update_mode not in POS_UPDATE_MODES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="update_mode must be UPDATE_HIDDEN_ONLY, UPDATE_IF_NO_RESERVATIONS, or SKIP_EXISTING.",
        )

    default_status = payload.default_product_status.strip().upper()
    if default_status not in POS_DEFAULT_PRODUCT_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="default_product_status must be HIDDEN for POS MVP sync.",
        )
    return update_mode, ProductStatus(default_status)


def _provider_for_integration(integration: PosIntegration, payload: MockPosSyncRequest) -> MockPosProvider | GenericPosProvider:
    if integration.provider == "MOCK_POS":
        return MockPosProvider(payload.mock_items)
    return GenericPosProvider()


def _pos_item_to_product_create(item: NormalizedPosItem, store_id: UUID, default_status: ProductStatus) -> ProductCreate:
    return ProductCreate(
        store_id=store_id,
        name=item.name.strip(),
        external_sku=item.external_sku.strip(),
        description=item.description.strip() if item.description else None,
        original_price=item.original_price,
        discount_price=item.discount_price,
        quantity=item.stock_quantity,
        allow_pickup=item.pickup_available,
        allow_quick_delivery=item.quick_delivery_available,
        allow_parcel_delivery=item.parcel_delivery_available,
        quick_delivery_fee=item.quick_delivery_fee,
        parcel_delivery_fee=item.parcel_delivery_fee,
        pickup_start_time=item.sale_starts_at,
        pickup_end_time=item.sale_ends_at,
        status=default_status,
    )


def _row_reason(code: str, message: str) -> str:
    return f"{code}: {message}"


def _missing_sku_reason() -> str:
    return _row_reason("MISSING_EXTERNAL_SKU", "external_sku가 없어 POS 동기화에서 처리할 수 없습니다.")


def _batch_status(created_count: int, updated_count: int, skipped_count: int, failed_count: int) -> str:
    success_count = created_count + updated_count + skipped_count
    if success_count == 0 and failed_count > 0:
        return "FAILED"
    if failed_count > 0:
        return "COMPLETED_WITH_ERRORS"
    return "COMPLETED"


def run_mock_pos_sync(db: Session, merchant: Merchant, payload: MockPosSyncRequest) -> MockPosSyncResult:
    integration = get_or_create_pos_integration(db, merchant)
    store = _get_owned_store(db, merchant, integration.store_id) if integration.store_id else _get_default_store(db, merchant)
    update_mode, default_status = _normalize_sync_policy(payload)
    provider = _provider_for_integration(integration, payload)
    is_valid, connection_message = provider.validate_connection()
    raw_items = provider.fetch_items()

    batch = PosSyncBatch(
        integration_id=integration.id,
        merchant_id=merchant.id,
        store_id=store.id,
        total_rows=len(raw_items),
    )
    db.add(batch)
    db.flush()

    created_count = 0
    updated_count = 0
    skipped_count = 0
    failed_count = 0

    if not is_valid:
        failed_count += 1
        db.add(
            PosSyncRow(
                batch_id=batch.id,
                action="FAILED",
                product_name=integration.provider,
                error_message=_row_reason(
                    connection_message or "PROVIDER_NOT_CONFIGURED",
                    "현재 provider는 실제 외부 POS 호출 없이 skeleton 상태입니다.",
                ),
            )
        )

    for raw_item in raw_items if is_valid else []:
        external_sku: str | None = None
        product_name: str | None = None
        try:
            normalized_item = provider.normalize_item(raw_item)
            external_sku = normalized_item.external_sku
            product_name = normalized_item.name
            if not normalized_item.external_sku:
                raise ValueError(_missing_sku_reason())
            product_payload = _pos_item_to_product_create(normalized_item, store.id, default_status)
            duplicate = _find_duplicate_product(db, merchant, product_payload)
            if duplicate is None:
                product = create_product_for_store(db, merchant, product_payload)
                created_count += 1
                row = PosSyncRow(
                    batch_id=batch.id,
                    external_sku=normalized_item.external_sku,
                    product_id=product.id,
                    action="CREATED",
                    product_name=product.name,
                )
            elif update_mode == "SKIP_EXISTING":
                skipped_count += 1
                row = PosSyncRow(
                    batch_id=batch.id,
                    external_sku=normalized_item.external_sku,
                    product_id=duplicate.id,
                    action="SKIPPED",
                    product_name=duplicate.name,
                    error_message=_row_reason("EXISTING_PRODUCT_SKIPPED_BY_POLICY", "동기화 정책에 따라 기존 상품을 건너뛰었습니다."),
                )
            elif update_mode == "UPDATE_HIDDEN_ONLY" and duplicate.status != ProductStatus.HIDDEN:
                skipped_count += 1
                row = PosSyncRow(
                    batch_id=batch.id,
                    external_sku=normalized_item.external_sku,
                    product_id=duplicate.id,
                    action="SKIPPED",
                    product_name=duplicate.name,
                    error_message=_row_reason("EXISTING_PRODUCT_NOT_HIDDEN", "숨김 상품만 업데이트하는 정책이라 건너뛰었습니다."),
                )
            elif _product_has_reservations(db, duplicate.id):
                skipped_count += 1
                row = PosSyncRow(
                    batch_id=batch.id,
                    external_sku=normalized_item.external_sku,
                    product_id=duplicate.id,
                    action="SKIPPED",
                    product_name=duplicate.name,
                    error_message=_row_reason("EXISTING_PRODUCT_HAS_RESERVATIONS", "예약이 있는 상품은 POS 동기화에서 자동 업데이트하지 않았습니다."),
                )
            else:
                _apply_import_update(duplicate, product_payload)
                updated_count += 1
                row = PosSyncRow(
                    batch_id=batch.id,
                    external_sku=normalized_item.external_sku,
                    product_id=duplicate.id,
                    action="UPDATED",
                    product_name=duplicate.name,
                )
        except (ValueError, ValidationError, HTTPException) as exc:
            failed_count += 1
            detail = exc.detail if isinstance(exc, HTTPException) else str(exc)
            detail_text = str(detail)
            if "discount_price" in detail_text and "greater than original_price" in detail_text:
                detail_text = _row_reason("INVALID_PRICE", "할인가가 원가보다 클 수 없습니다.")
            row = PosSyncRow(
                batch_id=batch.id,
                external_sku=external_sku,
                action="FAILED",
                product_name=product_name,
                error_message=detail_text,
            )
        db.add(row)

    batch.created_count = created_count
    batch.updated_count = updated_count
    batch.skipped_count = skipped_count
    batch.failed_count = failed_count
    batch.status = _batch_status(created_count, updated_count, skipped_count, failed_count)
    integration.last_synced_at = datetime.now(timezone.utc)
    integration.last_sync_status = batch.status
    integration.status = "ERROR" if batch.status == "FAILED" else "CONNECTED"
    integration.updated_at = datetime.now(timezone.utc)
    db.commit()

    refreshed = get_pos_sync_batch(db, merchant, batch.id)
    return MockPosSyncResult(
        batch_id=refreshed.id,
        total_rows=refreshed.total_rows,
        created_count=refreshed.created_count,
        updated_count=refreshed.updated_count,
        skipped_count=refreshed.skipped_count,
        failed_count=refreshed.failed_count,
        status=refreshed.status,
        rows=[row for row in refreshed.rows],
    )


def get_pos_sync_batches(db: Session, merchant: Merchant) -> list[PosSyncBatchRead]:
    batches = db.scalars(
        select(PosSyncBatch)
        .options(selectinload(PosSyncBatch.rows))
        .where(PosSyncBatch.merchant_id == merchant.id)
        .order_by(PosSyncBatch.created_at.desc())
        .limit(20)
    ).all()
    return [PosSyncBatchRead.model_validate(batch) for batch in batches]


def get_pos_sync_batch(db: Session, merchant: Merchant, batch_id: UUID) -> PosSyncBatchRead:
    batch = db.scalar(
        select(PosSyncBatch)
        .options(selectinload(PosSyncBatch.rows))
        .where(
            PosSyncBatch.id == batch_id,
            PosSyncBatch.merchant_id == merchant.id,
        )
    )
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="POS sync batch not found.")
    return PosSyncBatchRead.model_validate(batch)


def read_pos_integration(db: Session, merchant: Merchant) -> PosIntegrationRead:
    return PosIntegrationRead.model_validate(get_or_create_pos_integration(db, merchant))
