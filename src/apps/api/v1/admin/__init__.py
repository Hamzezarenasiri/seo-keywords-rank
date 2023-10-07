from fastapi import APIRouter

from .auth import admin_auth_router
from .city import router as city_router
from .file import file_router
from .keyword import keyword_router
from .profile import profile_router
from .state import router as state_router
from .users import user_router

admin_router = APIRouter()

admin_router.include_router(admin_auth_router, prefix="/auth")
admin_router.include_router(keyword_router, prefix="/keywords")
# admin_router.include_router(config_router, prefix="/configs")
# admin_router.include_router(device_router, prefix="/devices")
# admin_router.include_router(file_router, prefix="/files")
# admin_router.include_router(group_router, prefix="/groups")
admin_router.include_router(profile_router, prefix="/me")
# admin_router.include_router(language_router, prefix="/languages")
# admin_router.include_router(user_router, prefix="/users")
# admin_router.include_router(state_router, prefix="/states")
# admin_router.include_router(city_router, prefix="/cities")
