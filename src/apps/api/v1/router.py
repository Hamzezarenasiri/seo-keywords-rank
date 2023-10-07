from fastapi import APIRouter

from .admin import admin_router

router_v1 = APIRouter()
# router_v1.include_router(common_router, tags=["v1_Common"])
router_v1.include_router(admin_router, prefix="/admin", tags=["v1_Admin"])
# router_v1.include_router(client_router, tags=["v1_Client"])
