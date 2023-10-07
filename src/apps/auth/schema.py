from typing import Optional, Union, List

from pydantic import BaseModel, Field

from src.core.base.schema import BaseSchema
from src.core.mixins import DB_ID, ErrorMessage, Message
from src.core.mixins.fields import OptionalEmailStr
from src.core.mixins.models import UsernameSchema
from src.main.config import app_settings
from .enum import AuthErrorMessageEnum, AuthMessageEnum
from ..user.enum import GenderEnum


class AuthToken(BaseModel):
    access_token: str
    refresh_token: str


class AuthUsernamePasswordIn(UsernameSchema, BaseSchema):
    username: str = Field(example="+989123456789")
    password: str = Field(example="0123456789", min_length=3, max_length=50)


class AuthOTPVerifyIn(UsernameSchema, BaseSchema):
    verification_code: Optional[str] = Field(
        min_length=app_settings.OTP_LENGTH,
        max_length=app_settings.OTP_LENGTH,
        example="12345",
    )


class AuthUserForgetOtpReqIn(UsernameSchema, BaseSchema):
    pass


class AuthUserChangePasswordIn(BaseSchema):
    old_password: Optional[str] = Field(
        min_length=8, max_length=50, example="0123456789"
    )
    new_password: str = Field(min_length=8, max_length=50, example="0123456789")


class AuthUserResetPasswordOut(AuthToken):
    pass


class AuthChangedPasswordErrorMessageOut(ErrorMessage):
    detail: str = AuthErrorMessageEnum.changed_password


class AuthChangedPasswordMessageOut(Message):
    detail: str = AuthMessageEnum.changed_password


class AuthRegisterIn(BaseSchema, UsernameSchema):
    first_name: Optional[str]
    last_name: Optional[str]
    username: str = Field(example="+989123456789")
    password: str = Field(example="0123456789")
    gender: Optional[GenderEnum]
    # mobile_number: str = Field(example="+989123456789")
    # email: Optional[OptionalEmailStr]


class AuthRegisterOut(BaseSchema):
    id: DB_ID
    first_name: Optional[str]
    last_name: Optional[str]
    mobile_number: str
    email: Optional[OptionalEmailStr]


class AuthIDTokenInSchema(BaseModel):
    id_token: Union[str, bytes]


class AuthForgetVerifyOut(BaseSchema):
    access_token: str
    limited: Optional[bool]

    class Config(BaseSchema.Config):
        max_anystr_length = None


class UserGetLogoutOut(BaseSchema):
    force_login: bool


class PermissionItem(BaseSchema):
    entity: str
    rules: List[str]


class GroupCreateIn(BaseSchema):
    name: str
    permissions: List[PermissionItem]


class GroupCreateOut(BaseSchema):
    name: str
    permissions: List[PermissionItem]


class GroupGetListOut(BaseSchema):
    name: str
    permissions: List[PermissionItem]


class GroupGetOut(GroupCreateOut):
    pass


class GroupUpdateIn(BaseSchema):
    name: Optional[str]
    permissions: Optional[List[PermissionItem]]


class GroupUpdateOut(GroupCreateOut):
    pass


class CustomerRequestLoginOTPIn(UsernameSchema):
    username: str = Field(min_length=1)


class CustomerVerifyLoginOTPIn(UsernameSchema):
    verification_code: str = Field(
        min_length=app_settings.OTP_LENGTH,
        max_length=app_settings.OTP_LENGTH,
        example="12345",
    )
