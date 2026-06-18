from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.region import RegionProductRead
from app.schemas.store import StoreRead
from app.services.region_service import get_nearby_region_products, get_region_products, get_region_stores


router = APIRouter()


@router.get("/stores", response_model=list[StoreRead])
def list_region_stores(
    sido: str | None = Query(default=None),
    sigungu: str | None = Query(default=None),
    dong: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[StoreRead]:
    stores = get_region_stores(db, sido=sido, sigungu=sigungu, dong=dong)
    return [StoreRead.model_validate(store) for store in stores]


@router.get("/products", response_model=list[RegionProductRead])
def list_region_products(
    sido: str | None = Query(default=None),
    sigungu: str | None = Query(default=None),
    dong: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[RegionProductRead]:
    products = get_region_products(db, sido=sido, sigungu=sigungu, dong=dong)
    return [
        RegionProductRead(
            id=product.id,
            store_id=product.store_id,
            store_name=product.store.name,
            store_address=product.store.address,
            sido=product.store.sido,
            sigungu=product.store.sigungu,
            dong=product.store.dong,
            name=product.name,
            description=product.description,
            image_url=product.image_url,
            original_price=product.original_price,
            discount_price=product.discount_price,
            quantity=product.quantity,
            allow_pickup=product.allow_pickup,
            allow_quick_delivery=product.allow_quick_delivery,
            allow_parcel_delivery=product.allow_parcel_delivery,
            quick_delivery_fee=product.quick_delivery_fee,
            parcel_delivery_fee=product.parcel_delivery_fee,
            pickup_start_time=product.pickup_start_time,
            pickup_end_time=product.pickup_end_time,
            status=product.status,
        )
        for product in products
    ]


@router.get("/products/nearby", response_model=list[RegionProductRead])
def list_nearby_region_products(
    lat: float = Query(ge=-90, le=90),
    lng: float = Query(ge=-180, le=180),
    db: Session = Depends(get_db),
) -> list[RegionProductRead]:
    products = get_nearby_region_products(db, latitude=lat, longitude=lng)
    return [
        RegionProductRead(
            id=product.id,
            store_id=product.store_id,
            store_name=product.store.name,
            store_address=product.store.address,
            sido=product.store.sido,
            sigungu=product.store.sigungu,
            dong=product.store.dong,
            distance_km=round(distance_km, 2),
            name=product.name,
            description=product.description,
            image_url=product.image_url,
            original_price=product.original_price,
            discount_price=product.discount_price,
            quantity=product.quantity,
            allow_pickup=product.allow_pickup,
            allow_quick_delivery=product.allow_quick_delivery,
            allow_parcel_delivery=product.allow_parcel_delivery,
            quick_delivery_fee=product.quick_delivery_fee,
            parcel_delivery_fee=product.parcel_delivery_fee,
            pickup_start_time=product.pickup_start_time,
            pickup_end_time=product.pickup_end_time,
            status=product.status,
        )
        for product, distance_km in products
    ]
