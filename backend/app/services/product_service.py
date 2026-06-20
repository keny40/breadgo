import csv
import io
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.merchant import Merchant
from app.models.product import Product, ProductStatus
from app.models.product_import import ProductImportBatch, ProductImportRow
from app.models.recommendation_usage import RecommendationUsage
from app.models.reservation import Reservation
from app.models.store import Store
from app.schemas.product import (
    ProductCreate,
    ProductCsvImportError,
    ProductCsvImportResult,
    ProductCsvImportRowResult,
    ProductDuplicateCreate,
    ProductImportBatchRead,
    ProductUpdate,
)

KST = ZoneInfo("Asia/Seoul")
CSV_REQUIRED_COLUMNS = {
    "name",
    "original_price",
    "discount_price",
    "stock_quantity",
    "sale_starts_at",
    "sale_ends_at",
}
CSV_IMPORT_ACTIONS = {"CREATE_ONLY", "UPDATE_OR_CREATE", "SKIP_DUPLICATE"}


@dataclass
class CsvPlannedRow:
    row_result: ProductCsvImportRowResult
    payload: ProductCreate


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


def _sync_recommendation_usage_product_status(
    db: Session,
    product: Product,
    previous_status: ProductStatus | None = None,
) -> None:
    usage = db.scalar(select(RecommendationUsage).where(RecommendationUsage.created_product_id == product.id))
    if usage is None:
        return

    now = datetime.now(timezone.utc)
    if product.status == ProductStatus.ACTIVE:
        usage.draft_product_status = "PUBLISHED"
        if usage.published_at is None:
            usage.published_at = now
        return

    if product.status == ProductStatus.HIDDEN:
        usage.draft_product_status = "ARCHIVED" if previous_status == ProductStatus.ACTIVE else "HIDDEN_DRAFT"


def create_product_for_store(db: Session, merchant: Merchant, payload: ProductCreate) -> Product:
    _get_owned_store(db, merchant, payload.store_id)

    product = Product(
        store_id=payload.store_id,
        name=payload.name.strip(),
        external_sku=payload.external_sku.strip() if payload.external_sku else None,
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


def _decode_csv_content(content: bytes) -> str:
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return content.decode("cp949")


def _parse_csv_bool(value: str | None, default: bool) -> bool:
    if value is None or not value.strip():
        return default
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "y", "가능", "o", "ok"}:
        return True
    if normalized in {"false", "0", "no", "n", "불가", "x"}:
        return False
    raise ValueError("true/false, 1/0, 가능/불가 중 하나로 입력하세요.")


def _parse_csv_decimal(value: str | None, field: str) -> Decimal:
    if value is None or not value.strip():
        raise ValueError(f"{field} is required.")
    try:
        parsed = Decimal(value.strip())
    except InvalidOperation as exc:
        raise ValueError("숫자 형식으로 입력하세요.") from exc
    if parsed <= 0:
        raise ValueError("0보다 큰 금액을 입력하세요.")
    return parsed


def _parse_csv_fee(value: str | None) -> Decimal:
    if value is None or not value.strip():
        return Decimal("0.00")
    try:
        parsed = Decimal(value.strip())
    except InvalidOperation as exc:
        raise ValueError("숫자 형식으로 입력하세요.") from exc
    if parsed < 0:
        raise ValueError("0 이상 금액을 입력하세요.")
    return parsed


def _parse_csv_int(value: str | None, field: str) -> int:
    if value is None or not value.strip():
        raise ValueError(f"{field} is required.")
    try:
        parsed = int(value.strip())
    except ValueError as exc:
        raise ValueError("정수로 입력하세요.") from exc
    if parsed < 0:
        raise ValueError("0 이상 수량을 입력하세요.")
    return parsed


def _parse_csv_datetime(value: str | None, field: str) -> datetime:
    if value is None or not value.strip():
        raise ValueError(f"{field} is required.")
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError("YYYY-MM-DDTHH:MM 또는 YYYY-MM-DD HH:MM 형식으로 입력하세요.") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=KST)
    return parsed.astimezone(timezone.utc)


def _validate_csv_header(fieldnames: list[str] | None) -> None:
    columns = {field.strip() for field in (fieldnames or []) if field}
    missing = sorted(CSV_REQUIRED_COLUMNS - columns)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required CSV columns: {', '.join(missing)}",
        )


def _normalize_import_action(value: str | None, default_import_action: str) -> str:
    raw_value = value.strip().upper() if value else default_import_action
    if raw_value not in CSV_IMPORT_ACTIONS:
        raise ValueError("import_action은 CREATE_ONLY, UPDATE_OR_CREATE, SKIP_DUPLICATE 중 하나여야 합니다.")
    return raw_value


def _row_to_product_create(row: dict[str, str | None], store_id: UUID) -> ProductCreate:
    name = (row.get("name") or "").strip()
    if not name:
        raise ValueError("name is required.")

    original_price = _parse_csv_decimal(row.get("original_price"), "original_price")
    discount_price = _parse_csv_decimal(row.get("discount_price"), "discount_price")
    quantity = _parse_csv_int(row.get("stock_quantity"), "stock_quantity")
    pickup_start_time = _parse_csv_datetime(row.get("sale_starts_at"), "sale_starts_at")
    pickup_end_time = _parse_csv_datetime(row.get("sale_ends_at"), "sale_ends_at")
    allow_pickup = _parse_csv_bool(row.get("pickup_available"), True)
    allow_quick_delivery = _parse_csv_bool(row.get("quick_delivery_available"), False)
    allow_parcel_delivery = _parse_csv_bool(row.get("parcel_delivery_available"), False)

    return ProductCreate(
        store_id=store_id,
        name=name,
        external_sku=(row.get("external_sku") or row.get("sku") or "").strip() or None,
        description=(row.get("description") or "").strip() or None,
        image_url=(row.get("image_url") or "").strip() or None,
        original_price=original_price,
        discount_price=discount_price,
        quantity=quantity,
        allow_pickup=allow_pickup,
        allow_quick_delivery=allow_quick_delivery,
        allow_parcel_delivery=allow_parcel_delivery,
        quick_delivery_fee=_parse_csv_fee(row.get("quick_delivery_fee")),
        parcel_delivery_fee=_parse_csv_fee(row.get("parcel_delivery_fee")),
        pickup_start_time=pickup_start_time,
        pickup_end_time=pickup_end_time,
        status=ProductStatus.HIDDEN,
    )


def _find_duplicate_product(db: Session, merchant: Merchant, payload: ProductCreate) -> Product | None:
    if payload.external_sku:
        product = db.scalar(
            select(Product)
            .join(Store, Product.store_id == Store.id)
            .where(
                Store.merchant_id == merchant.id,
                Product.store_id == payload.store_id,
                Product.external_sku == payload.external_sku,
            )
            .order_by(Product.created_at.desc())
        )
        if product is not None:
            return product

    return db.scalar(
        select(Product)
        .join(Store, Product.store_id == Store.id)
        .where(
            Store.merchant_id == merchant.id,
            Product.store_id == payload.store_id,
            Product.name == payload.name,
            Product.pickup_start_time == payload.pickup_start_time,
        )
        .order_by(Product.created_at.desc())
    )


def _product_has_reservations(db: Session, product_id: UUID) -> bool:
    return db.scalar(select(Reservation.id).where(Reservation.product_id == product_id).limit(1)) is not None


def _apply_import_update(product: Product, payload: ProductCreate) -> None:
    product.external_sku = payload.external_sku
    product.description = payload.description
    product.image_url = payload.image_url
    product.original_price = payload.original_price
    product.discount_price = payload.discount_price
    product.quantity = payload.quantity
    product.allow_pickup = payload.allow_pickup
    product.allow_quick_delivery = payload.allow_quick_delivery
    product.allow_parcel_delivery = payload.allow_parcel_delivery
    product.quick_delivery_fee = payload.quick_delivery_fee
    product.parcel_delivery_fee = payload.parcel_delivery_fee
    product.pickup_start_time = payload.pickup_start_time
    product.pickup_end_time = payload.pickup_end_time
    _apply_sold_out_status(product)


def _batch_status(success_count: int, failed_count: int) -> str:
    if success_count == 0 and failed_count > 0:
        return "FAILED"
    if failed_count > 0:
        return "COMPLETED_WITH_ERRORS"
    return "COMPLETED"


def import_products_from_csv(
    db: Session,
    merchant: Merchant,
    store_id: UUID,
    content: bytes,
    *,
    preview: bool,
    file_name: str = "products.csv",
    default_import_action: str = "CREATE_ONLY",
) -> ProductCsvImportResult:
    _get_owned_store(db, merchant, store_id)
    default_import_action = _normalize_import_action(default_import_action, "CREATE_ONLY")
    text = _decode_csv_content(content)
    reader = csv.DictReader(io.StringIO(text))
    _validate_csv_header(reader.fieldnames)

    created_product_ids: list[UUID] = []
    errors: list[ProductCsvImportError] = []
    rows: list[ProductCsvImportRowResult] = []
    planned_rows: list[CsvPlannedRow] = []
    created_count = 0
    updated_count = 0
    skipped_count = 0
    total_rows = 0

    for row_number, row in enumerate(reader, start=2):
        if not any((value or "").strip() for value in row.values()):
            continue
        total_rows += 1
        try:
            import_action = _normalize_import_action(row.get("import_action"), default_import_action)
            payload = _row_to_product_create(row, store_id)
            duplicate = _find_duplicate_product(db, merchant, payload)
            duplicate_detected = duplicate is not None
            action_candidate = "CREATED"
            product_id: UUID | None = None

            if duplicate_detected and duplicate is not None:
                product_id = duplicate.id
                if import_action == "UPDATE_OR_CREATE":
                    if _product_has_reservations(db, duplicate.id):
                        action_candidate = "SKIPPED"
                    else:
                        action_candidate = "UPDATED"
                else:
                    action_candidate = "SKIPPED"

            if action_candidate == "CREATED":
                created_count += 1
            elif action_candidate == "UPDATED":
                updated_count += 1
            elif action_candidate == "SKIPPED":
                skipped_count += 1

            row_result = ProductCsvImportRowResult(
                row_number=row_number,
                product_id=product_id,
                product_name=payload.name,
                action=action_candidate if preview else "PENDING",
                action_candidate=action_candidate,
                duplicate_detected=duplicate_detected,
                error_message=(
                    "예약이 있는 기존 상품은 CSV로 업데이트하지 않고 건너뜁니다."
                    if duplicate_detected
                    and duplicate is not None
                    and import_action == "UPDATE_OR_CREATE"
                    and _product_has_reservations(db, duplicate.id)
                    else None
                ),
            )
            rows.append(row_result)
            planned_rows.append(CsvPlannedRow(row_result=row_result, payload=payload))
        except (ValueError, ValidationError) as exc:
            field = "row"
            message = str(exc)
            for candidate in CSV_REQUIRED_COLUMNS:
                if candidate in message:
                    field = candidate
                    break
            errors.append(ProductCsvImportError(row_number=row_number, field=field, message=message))
            rows.append(
                ProductCsvImportRowResult(
                    row_number=row_number,
                    product_name=(row.get("name") or "").strip() or None,
                    action="FAILED",
                    action_candidate="FAILED",
                    duplicate_detected=False,
                    error_message=message,
                )
            )

    if not preview:
        created_product_ids = []
        created_count = 0
        updated_count = 0
        skipped_count = 0

        for planned_row in planned_rows:
            row_result = planned_row.row_result
            try:
                payload = planned_row.payload
                duplicate = _find_duplicate_product(db, merchant, payload)
                if row_result.action_candidate == "CREATED":
                    product = create_product_for_store(db, merchant, payload)
                    row_result.product_id = product.id
                    row_result.action = "CREATED"
                    created_product_ids.append(product.id)
                    created_count += 1
                elif row_result.action_candidate == "UPDATED" and duplicate is not None:
                    _apply_import_update(duplicate, payload)
                    row_result.product_id = duplicate.id
                    row_result.action = "UPDATED"
                    updated_count += 1
                else:
                    row_result.action = "SKIPPED"
                    skipped_count += 1
            except (ValueError, ValidationError) as exc:
                row_result.action = "FAILED"
                row_result.action_candidate = "FAILED"
                row_result.error_message = str(exc)
                errors.append(ProductCsvImportError(row_number=row_result.row_number, field="row", message=str(exc)))

        success_count = created_count + updated_count + skipped_count
        failed_count = len(errors)
        batch = ProductImportBatch(
            merchant_id=merchant.id,
            store_id=store_id,
            file_name=file_name[:255] or "products.csv",
            total_rows=total_rows,
            success_count=success_count,
            failed_count=failed_count,
            created_count=created_count,
            updated_count=updated_count,
            skipped_count=skipped_count,
            status=_batch_status(success_count, failed_count),
        )
        db.add(batch)
        db.flush()

        for row_result in rows:
            db.add(
                ProductImportRow(
                    batch_id=batch.id,
                    row_number=row_result.row_number,
                    product_id=row_result.product_id,
                    action=row_result.action,
                    product_name=row_result.product_name,
                    error_message=row_result.error_message,
                )
            )

        db.commit()
        return ProductCsvImportResult(
            batch_id=batch.id,
            total_rows=total_rows,
            success_count=success_count,
            failed_count=failed_count,
            created_count=created_count,
            updated_count=updated_count,
            skipped_count=skipped_count,
            created_product_ids=created_product_ids,
            errors=errors,
            rows=rows,
        )

    success_count = created_count + updated_count + skipped_count
    failed_count = len(errors)
    return ProductCsvImportResult(
        batch_id=None,
        total_rows=total_rows,
        success_count=success_count,
        failed_count=failed_count,
        created_count=created_count,
        updated_count=updated_count,
        skipped_count=skipped_count,
        created_product_ids=created_product_ids,
        errors=errors,
        rows=rows,
    )


def get_product_import_batches(db: Session, merchant: Merchant) -> list[ProductImportBatch]:
    return list(
        db.scalars(
            select(ProductImportBatch)
            .where(ProductImportBatch.merchant_id == merchant.id)
            .order_by(ProductImportBatch.created_at.desc())
            .limit(30)
        )
    )


def get_product_import_batch(db: Session, merchant: Merchant, batch_id: UUID) -> ProductImportBatchRead:
    from sqlalchemy.orm import selectinload

    batch = db.scalar(
        select(ProductImportBatch)
        .where(ProductImportBatch.id == batch_id, ProductImportBatch.merchant_id == merchant.id)
        .options(selectinload(ProductImportBatch.rows))
    )
    if batch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Import batch not found.")
    return ProductImportBatchRead.model_validate(batch)


def duplicate_product_for_merchant(
    db: Session,
    merchant: Merchant,
    product_id: UUID,
    payload: ProductDuplicateCreate,
) -> Product:
    original = _get_owned_product(db, merchant, product_id)
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    default_end = now + timedelta(hours=3)
    pickup_start_time = payload.sale_starts_at or now
    pickup_end_time = payload.sale_ends_at or default_end

    if pickup_start_time >= pickup_end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sale_starts_at must be earlier than sale_ends_at.",
        )

    suffix = payload.name_suffix.strip() if payload.name_suffix else ""
    copied_name = f"{original.name} {suffix}".strip() if suffix else original.name
    quantity = payload.stock_quantity if payload.stock_quantity is not None else max(original.quantity, 1)

    product = Product(
        store_id=original.store_id,
        name=copied_name,
        description=original.description,
        image_url=original.image_url,
        original_price=original.original_price,
        discount_price=original.discount_price,
        quantity=quantity,
        allow_pickup=original.allow_pickup,
        allow_quick_delivery=original.allow_quick_delivery,
        allow_parcel_delivery=original.allow_parcel_delivery,
        quick_delivery_fee=original.quick_delivery_fee,
        parcel_delivery_fee=original.parcel_delivery_fee,
        pickup_start_time=pickup_start_time,
        pickup_end_time=pickup_end_time,
        status=ProductStatus.ACTIVE if payload.is_visible else ProductStatus.HIDDEN,
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
    previous_status = product.status
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
    _sync_recommendation_usage_product_status(db, product, previous_status)
    db.commit()
    db.refresh(product)
    return product


def hide_product(db: Session, merchant: Merchant, product_id: UUID) -> Product:
    product = _get_owned_product(db, merchant, product_id)
    previous_status = product.status
    product.status = ProductStatus.HIDDEN
    _sync_recommendation_usage_product_status(db, product, previous_status)
    db.commit()
    db.refresh(product)
    return product
