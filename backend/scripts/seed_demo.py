import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.merchant import Merchant, MerchantStatus
from app.models.product import Product, ProductStatus
from app.models.store import Store
from app.models.user import User, UserRole


DEMO_PASSWORD = "12345678"


def upsert_user(db: Session, email: str, full_name: str, role: UserRole) -> User:
    user = db.scalar(select(User).where(User.email == email))
    password_hash = get_password_hash(DEMO_PASSWORD)
    if user is None:
        user = User(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            is_active=True,
        )
        db.add(user)
    else:
        user.password_hash = password_hash
        user.full_name = full_name
        user.role = role
        user.is_active = True
    db.flush()
    return user


def upsert_merchant(db: Session, merchant_user: User) -> Merchant:
    merchant = db.scalar(select(Merchant).where(Merchant.user_id == merchant_user.id))
    if merchant is None:
        merchant = Merchant(user_id=merchant_user.id)
        db.add(merchant)

    merchant.business_name = "브레드고 데모 베이커리"
    merchant.business_registration_number = "111-22-33333"
    merchant.representative_name = "데모점주"
    merchant.phone_number = "010-1111-2222"
    merchant.status = MerchantStatus.APPROVED
    db.flush()
    return merchant


def upsert_store(db: Session, merchant: Merchant, payload: dict[str, str]) -> Store:
    store = db.scalar(
        select(Store).where(
            Store.merchant_id == merchant.id,
            Store.name == payload["name"],
        )
    )
    if store is None:
        store = Store(merchant_id=merchant.id, name=payload["name"])
        db.add(store)

    store.address = payload["address"]
    store.address_detail = None
    store.sido = payload["sido"]
    store.sigungu = payload["sigungu"]
    store.dong = payload["dong"]
    store.latitude = Decimal(payload["latitude"])
    store.longitude = Decimal(payload["longitude"])
    store.phone_number = "02-1234-5678"
    store.description = f"{payload['dong']} 데모 픽업 매장입니다."
    store.opening_time = datetime.strptime("09:00", "%H:%M").time()
    store.closing_time = datetime.strptime("21:00", "%H:%M").time()
    store.is_active = True
    db.flush()
    return store


def upsert_product(
    db: Session,
    store: Store,
    name: str,
    original_price: Decimal,
    discount_price: Decimal,
    quantity: int,
    pickup_start_time: datetime,
    pickup_end_time: datetime,
) -> Product:
    product = db.scalar(
        select(Product).where(
            Product.store_id == store.id,
            Product.name == name,
        )
    )
    if product is None:
        product = Product(store_id=store.id, name=name)
        db.add(product)

    product.description = f"{store.name}의 {name}입니다."
    product.original_price = original_price
    product.discount_price = discount_price
    product.quantity = quantity
    product.pickup_start_time = pickup_start_time
    product.pickup_end_time = pickup_end_time
    product.status = ProductStatus.ACTIVE
    db.flush()
    return product


def seed_demo_data(db: Session) -> dict[str, int]:
    admin = upsert_user(db, "admin@breadgo.test", "BreadGo Admin", UserRole.ADMIN)
    merchant_user = upsert_user(db, "merchant@breadgo.test", "Demo Merchant", UserRole.MERCHANT)
    customer = upsert_user(db, "customer@breadgo.test", "Demo Customer", UserRole.CUSTOMER)
    merchant = upsert_merchant(db, merchant_user)

    stores_payload = [
        {
            "name": "브레드고 역삼점",
            "sido": "서울특별시",
            "sigungu": "강남구",
            "dong": "역삼동",
            "address": "서울특별시 강남구 테헤란로 123",
            "latitude": "37.500000",
            "longitude": "127.036000",
        },
        {
            "name": "브레드고 삼성점",
            "sido": "서울특별시",
            "sigungu": "강남구",
            "dong": "삼성동",
            "address": "서울특별시 강남구 삼성로 123",
            "latitude": "37.514000",
            "longitude": "127.056000",
        },
        {
            "name": "브레드고 고잔점",
            "sido": "경기도",
            "sigungu": "안산시",
            "dong": "고잔동",
            "address": "경기도 안산시 단원구 고잔로 123",
            "latitude": "37.318000",
            "longitude": "126.831000",
        },
    ]

    stores = [upsert_store(db, merchant, payload) for payload in stores_payload]

    now = datetime.now(timezone.utc)
    pickup_start = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=2)
    pickup_end = pickup_start + timedelta(hours=3)
    product_templates = [
        ("식빵 마감 세트", Decimal("9000"), Decimal("4500"), 8),
        ("크루아상 세트", Decimal("12000"), Decimal("5900"), 6),
        ("샌드위치 박스", Decimal("15000"), Decimal("7900"), 5),
        ("디저트 랜덤박스", Decimal("18000"), Decimal("8900"), 7),
    ]

    product_count = 0
    for index, store in enumerate(stores):
        templates = product_templates[: 3 if index == 0 else 2]
        for name, original_price, discount_price, quantity in templates:
            upsert_product(
                db=db,
                store=store,
                name=name,
                original_price=original_price,
                discount_price=discount_price,
                quantity=quantity,
                pickup_start_time=pickup_start,
                pickup_end_time=pickup_end,
            )
            product_count += 1

    db.commit()
    return {
        "users": 3,
        "merchant": 1,
        "stores": len(stores),
        "products": product_count,
        "admin_user_id": str(admin.id),
        "merchant_user_id": str(merchant_user.id),
        "customer_user_id": str(customer.id),
    }


def main() -> None:
    with SessionLocal() as db:
        result = seed_demo_data(db)
    print("BreadGo demo data seeded.")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
