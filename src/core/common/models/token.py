from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Field, validator

from src.core.common.enums import RoleEnum
from src.core.mixins import SchemaID
from src.main.config import jwt_settings


class AuthToken(BaseModel):
    access_token: str
    refresh_token: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPayload(BaseModel):
    user_id: Optional[str]
    role: Optional[RoleEnum]
    encrypted_values: Optional[str]
    limited: Optional[bool]
    exp: int = Field(
        default_factory=lambda: datetime.utcnow()
        + timedelta(seconds=jwt_settings.ACCESS_TOKEN_LIFETIME_SECONDS)
    )

    # This validator is needed, because it raises type_error otherwise
    @validator("user_id", pre=True)
    @classmethod
    def uuid_to_str(cls, value):
        if isinstance(value, SchemaID):
            return str(value)
        return value
