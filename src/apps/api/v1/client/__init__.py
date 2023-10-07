from fastapi import APIRouter

from .auth import router as auth_router
from .city import router as city_router

# from .config import config_router
from .file import file_router
from .profile import profile_router
from .state import router as state_router
from .user import router as user_router

client_router = APIRouter()
client_router.include_router(auth_router, prefix="/auth")
# client_router.include_router(config_router, prefix="/configs")
# client_router.include_router(file_router, prefix="/files")
# client_router.include_router(language_router, prefix="/languages")
client_router.include_router(profile_router, prefix="/me")
# client_router.include_router(state_router, prefix="/states")
# client_router.include_router(city_router, prefix="/cities")
# client_router.include_router(user_router, prefix="/users")
