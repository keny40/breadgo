from fastapi import APIRouter

from app.api.v1 import (
    admin,
    auth,
    merchants,
    notifications,
    ops,
    payments,
    pro_dashboard,
    products,
    regions,
    reservations,
    settlement_accounts,
    settlements,
    stores,
)


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(
    settlement_accounts.admin_router,
    prefix="/admin/merchants",
    tags=["settlement-accounts"],
)
api_router.include_router(settlements.admin_router, prefix="/admin/settlements", tags=["settlements"])
api_router.include_router(settlements.merchant_router, prefix="/merchant/settlements", tags=["settlements"])
api_router.include_router(
    settlement_accounts.router,
    prefix="/merchant/settlement-account",
    tags=["settlement-accounts"],
)
api_router.include_router(merchants.router, prefix="/merchants", tags=["merchants"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(ops.router, prefix="/ops", tags=["ops"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(pro_dashboard.router, prefix="/merchant/pro", tags=["merchant-pro"])
api_router.include_router(stores.router, prefix="/stores", tags=["stores"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(products.merchant_router, prefix="/merchant/products", tags=["products"])
api_router.include_router(products.store_router, prefix="/stores", tags=["products"])
api_router.include_router(regions.router, prefix="/regions", tags=["regions"])
api_router.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
api_router.include_router(reservations.merchant_router, prefix="/merchant/reservations", tags=["reservations"])
api_router.include_router(reservations.store_router, prefix="/stores", tags=["reservations"])
