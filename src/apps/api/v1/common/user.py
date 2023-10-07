from fastapi import (
    APIRouter,
)

from src.main.config import collections_names

entity = collections_names.USERS
router = APIRouter()
