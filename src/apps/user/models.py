from datetime import date, datetime
from typing import List, Optional, Union

import pymongo
from pydantic import BaseModel, Field, validator

from src.apps.auth.models import PermissionModel
from src.apps.language.enum import LanguageEnum
from src.apps.user.enum import (
    AddressType,
    DefaultGroupNameEnum,
    GenderEnum,
    LoginType,
    UserStatus,
    UserType,
    DeviceType,
    BusinessTypeEnum,
    UserBlockReasonEnum,
)
from src.core import mixins
from src.core.base.models import BaseDBReadModel, BaseDBModel
from src.core.common.enums import RoleEnum
from src.core.mixins import DB_ID, default_id
from src.core.mixins.fields import OptionalEmailStr, PointField, SchemaID
from src.main.config import app_settings, collections_names
from src.main.enums import (
    CountryCode,
    CurrencyCode,
)


class DeviceDetail(BaseModel):
    ua_string: str
    os: Optional[str]
    browser: Optional[str]
    device: Optional[str]


class UserDevicesModel(BaseModel):
    notification_token: str
    device_type: Optional[DeviceType]
    notification_enabled: bool = True
    device_detail: Optional[DeviceDetail]


class AddressModel(BaseModel):
    address_id: DB_ID
    address_name: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]
    location: Optional[PointField]
    address_line_1: Optional[str]
    address_line_2: Optional[str]
    town: Optional[str]
    building_name: Optional[str]
    apartment_number: Optional[str]
    country_code: Optional[str] = "UAE"
    is_default: Optional[bool] = False
    postal_code: Optional[str]
    alternate_phone_number: Optional[str]
    type: Optional[AddressType]
    state: Optional[str]
    city: Optional[str]
    area: Optional[str]
    street: Optional[str]
    landmark: Optional[str]


class AddressCreateModel(AddressModel):
    address_id: DB_ID = Field(default_factory=default_id)
    address_name: Optional[str] = "My Address"


class UserSettings(BaseModel):
    language: LanguageEnum
    country_code: CountryCode
    currency_code: Optional[CurrencyCode] = app_settings.DEFAULT_CURRENCY_CODE
    state: Optional[str]


class BlockInfoModel(BaseModel):
    blocked_by: SchemaID
    reason_type: List[UserBlockReasonEnum]
    description: Optional[str]
    blocked_datetime: datetime = Field(default_factory=datetime.utcnow)


class UserBaseModel(
    mixins.EmailModelMixin,
    mixins.IsEnableMixin,
    mixins.SoftDeleteMixin,
    mixins.PhoneNumberModelMixin,
    BaseDBModel,
):
    addresses: Optional[List[AddressModel]] = []
    avatar: Optional[str]
    date_of_birth: Optional[date]
    email: Optional[OptionalEmailStr]
    first_name: Optional[str]
    gender: Optional[GenderEnum]
    groups: List[Union[str, DefaultGroupNameEnum]]
    hashed_password: Optional[str]
    is_blocked: Optional[bool] = False
    block_info: Optional[BlockInfoModel]
    is_force_change_password: Optional[bool]
    last_login_datetime: Optional[datetime]
    last_name: Optional[str]
    login_datetime: Optional[datetime]
    national_code: Optional[str]
    permissions: Optional[List[PermissionModel]]
    mobile_number: Optional[str]
    settings: UserSettings
    telephone: Optional[str]
    login_type: Optional[LoginType]
    user_status: Optional[UserStatus]
    user_type: Optional[UserType]
    devices: List[UserDevicesModel]
    phone_verified: Optional[bool]
    email_verified: Optional[bool]
    business_type: Optional[BusinessTypeEnum] = BusinessTypeEnum.PERSONAL
    nick_name: str = "keywords projectuser"

    # pylint: disable=no-self-argument,no-self-use
    @validator("date_of_birth")
    def isoformat_time(cls, value: date) -> str:
        return value.isoformat() if value else None

    class Config(BaseModel.Config):
        arbitrary_types_allowed = True

    class Meta:
        collection_name = collections_names.USERS
        entity_name = "user"
        indexes = [
            pymongo.IndexModel([("email", pymongo.ASCENDING)], name="email"),
            pymongo.IndexModel(
                [("mobile_number", pymongo.ASCENDING)], name="mobile_number"
            ),
            pymongo.IndexModel("id", name="user_id", unique=True),
        ]


class UserDBReadModel(UserBaseModel, BaseDBReadModel):
    id: DB_ID
    is_blocked: bool
    is_deleted: bool
    is_enable: bool
    is_force_change_password: bool
    is_force_login: bool
    role: RoleEnum
    devices: Optional[List[UserDevicesModel]] = []


class UserDBCreateModel(UserBaseModel, mixins.CreateDatetimeMixin):
    id: DB_ID = Field(default_factory=default_id)
    addresses: Optional[List[AddressCreateModel]] = []
    devices: Optional[List[UserDevicesModel]] = []
    hashed_password: Optional[str]
    is_force_change_password: Optional[bool] = True
    is_force_login: Optional[bool] = False
    permissions: Optional[List[PermissionModel]] = []
    role: RoleEnum = Field(RoleEnum.customer.value)
    user_status: Optional[UserStatus] = UserStatus.just_joined.value
    settings: Optional[UserSettings] = UserSettings(
        language=app_settings.DEFAULT_LANGUAGE,
        country_code=app_settings.DEFAULT_COUNTRY_CODE,
    ).dict()
    phone_verified: Optional[bool] = False
    email_verified: Optional[bool] = False


class UserDBUpdateModel(UserBaseModel, mixins.UpdateDatetimeMixin):
    devices: Optional[List[UserDevicesModel]]
    is_blocked: Optional[bool]
    is_deleted: Optional[bool]
    is_enable: Optional[bool]
    is_force_change_password: Optional[bool]
    is_force_login: Optional[bool]
    mobile_number: Optional[str]
    settings: Optional[UserSettings]
    groups: Optional[List[Union[str, DefaultGroupNameEnum]]]
    addresses: Optional[List[AddressCreateModel]]
    role: Optional[RoleEnum]
    nick_name: Optional[str]
