from fastapi import APIRouter
from .auth import auth_router

from .user import router as user_router

common_router = APIRouter()

common_router.include_router(auth_router, prefix="/auth")
common_router.include_router(user_router, prefix="/users")
