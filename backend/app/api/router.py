from fastapi import APIRouter

from app.api.v1 import admin, auth, merchants, payments, products, regions, reservations, stores


api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(merchants.router, prefix="/merchants", tags=["merchants"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(stores.router, prefix="/stores", tags=["stores"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(products.store_router, prefix="/stores", tags=["products"])
api_router.include_router(regions.router, prefix="/regions", tags=["regions"])
api_router.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
api_router.include_router(reservations.store_router, prefix="/stores", tags=["reservations"])
