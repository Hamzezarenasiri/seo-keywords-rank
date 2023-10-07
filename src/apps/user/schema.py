from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Union, Dict

import phonenumbers
from pydantic import BaseModel, Field, HttpUrl, validator

from src.apps.auth.models import PermissionModel
from src.apps.user.enum import (
    AddressType,
    DefaultGroupNameEnum,
    GenderEnum,
    LoginType,
    UserStatus,
    DeviceType,
    UserType,
    BusinessTypeEnum,
    UserBlockReasonEnum,
)
from src.apps.user.models import UserDBReadModel, UserSettings
from src.core.base.schema import BaseSchema, PaginatedListSchema
from src.core.common.enums import RoleEnum
from src.core.mixins import SchemaID
from src.core.mixins.fields import OptionalEmailStr, PointField
from src.main.config import app_settings, region_settings
from src.main.enums import (
    CountryCode,
)


class AddressSchemaIn(BaseSchema):
    address_line_1: str = Field(min_length=2, max_length=320)
    address_line_2: Optional[str] = Field(min_length=2, max_length=320)
    address_name: Optional[str] = "My Address"
    alternate_phone_number: Optional[str]
    apartment_number: Optional[str]
    area: Optional[str]
    building_name: Optional[str]
    city: Optional[str]
    country_code: Optional[str]
    first_name: Optional[str]
    is_default: Optional[bool] = False
    landmark: Optional[str]
    last_name: Optional[str]
    location: Optional[PointField]
    phone_number: Optional[str]
    postal_code: Optional[str]
    state: Optional[str]
    street: Optional[str]
    town: str
    type: Optional[AddressType]


class AddressSchemaOut(AddressSchemaIn):
    address_id: SchemaID
    first_name: Optional[str]
    last_name: Optional[str]
    country_code: Optional[str]
    phone_number: Optional[str]
    alternate_phone_number: Optional[str]
    location: Optional[PointField]
    street: Optional[str]
    address_line_1: Optional[str]
    address_line_2: Optional[str]
    state: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    is_default: Optional[bool] = False
    type: Optional[AddressType]
    landmark: Optional[str]
    address_name: Optional[str]
    building_name: Optional[str]
    area: Optional[str]
    town: Optional[str]
    apartment_number: Optional[str]


class BlockInfo(BaseSchema):
    blocked_by: SchemaID
    reason_type: List[UserBlockReasonEnum]
    description: Optional[str]
    blocked_datetime: datetime


class BlockInfoSchemaIn(BaseSchema):
    reason_type: List[UserBlockReasonEnum]
    description: Optional[str]


class BaseUserSchema(BaseSchema):
    first_name: Optional[str] = Field(example="John")
    last_name: Optional[str] = Field(example="Doe")
    email: Optional[OptionalEmailStr] = Field(example="user@fanpino.com")
    mobile_number: Optional[str] = Field(example="+989123456789")
    is_enable: Optional[bool] = True

    @validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: str):
        if not value:
            return value
        try:
            mobile_number_obj = phonenumbers.parse(value, region_settings.DEFAULT)
            return phonenumbers.format_number(
                mobile_number_obj,
                phonenumbers.PhoneNumberFormat.E164,
            )
        except phonenumbers.NumberParseException as e:
            raise ValueError("Invalid Phone Number") from e


class CreateUserRoleEnum(str, Enum):
    admin: str = RoleEnum.admin.value
    customer: str = RoleEnum.customer.value
    audit: str = RoleEnum.audit.value


class CreateUserGroupEnum(str, Enum):
    admin: str = DefaultGroupNameEnum.admin.value
    customer: str = DefaultGroupNameEnum.customer.value
    audit: str = DefaultGroupNameEnum.audit.value


class UsersCreateOut(BaseUserSchema):
    id: SchemaID


class UsersCreateAdminIn(BaseUserSchema):
    first_name: str = Field(example="John")
    last_name: str = Field(example="Doe")
    password: str = Field(example="0123456789")
    national_code: Optional[str]
    addresses: List[AddressSchemaIn] = []
    avatar: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[GenderEnum]
    is_blocked: Optional[bool] = False
    is_force_change_password: Optional[bool] = True
    is_force_login: Optional[bool] = False
    national_code: Optional[str]
    permissions: Optional[List[PermissionModel]]
    settings: Optional[UserSettings] = UserSettings(
        language=app_settings.DEFAULT_LANGUAGE,
        country_code=app_settings.DEFAULT_COUNTRY_CODE,
    ).dict()
    telephone: Optional[str]
    user_status: Optional[UserStatus]


class UserCreateAdminCustomerIn(UsersCreateAdminIn):
    business_type: Optional[BusinessTypeEnum] = BusinessTypeEnum.PERSONAL.value


class UserCreateSchema(UsersCreateAdminIn):
    role: Optional[CreateUserRoleEnum]
    groups: Optional[List[Union[str, CreateUserGroupEnum]]] = []
    business_type: Optional[BusinessTypeEnum]
    nick_name: Optional[str]


class UserSocialCreateSchema(UsersCreateAdminIn):
    first_name: Optional[str] = Field(example="John")
    last_name: Optional[str] = Field(example="Doe")
    role: Optional[CreateUserRoleEnum]
    groups: Optional[List[Union[str, CreateUserGroupEnum]]] = []
    business_type: Optional[BusinessTypeEnum]
    nick_name: Optional[str]


class UserCreateSchemaOut(BaseUserSchema):
    id: SchemaID
    addresses: Optional[List[AddressSchemaOut]]
    avatar: Optional[str]
    date_of_birth: Optional[date]
    first_name: Optional[str] = Field(example="John")
    last_name: Optional[str] = Field(example="Doe")
    gender: Optional[GenderEnum]
    national_code: Optional[str]
    is_blocked: Optional[bool] = False
    is_force_change_password: Optional[bool]
    is_force_login: Optional[bool] = False
    national_code: Optional[str]
    permissions: Optional[List[PermissionModel]]
    settings: Optional[UserSettings]
    telephone: Optional[str]
    user_status: Optional[UserStatus]
    groups: List[Optional[Union[str, CreateUserGroupEnum]]] = [
        CreateUserGroupEnum.admin.value
    ]
    role: Optional[CreateUserRoleEnum]
    login_type: Optional[LoginType]
    last_login_datetime: Optional[datetime]
    login_datetime: Optional[datetime]
    business_type: Optional[BusinessTypeEnum]
    nick_name: Optional[str]
    create_datetime: datetime
    block_info: Optional[BlockInfo]


class UsersCreateAdminOut(BaseUserSchema):
    id: SchemaID
    addresses: Optional[List[AddressSchemaOut]]
    avatar: Optional[str]
    date_of_birth: Optional[date]
    first_name: Optional[str] = Field(example="John")
    last_name: Optional[str] = Field(example="Doe")
    gender: Optional[GenderEnum]
    national_code: Optional[str]
    is_blocked: Optional[bool] = False
    is_force_change_password: Optional[bool]
    is_force_login: Optional[bool] = False
    national_code: Optional[str]
    permissions: Optional[List[PermissionModel]]
    settings: Optional[UserSettings]
    telephone: Optional[str]
    user_status: Optional[UserStatus]
    groups: List[Optional[Union[str, CreateUserGroupEnum]]]
    role: Optional[CreateUserRoleEnum]
    business_type: Optional[BusinessTypeEnum]
    nick_name: Optional[str]


class UsersGetUserOut(UserCreateSchemaOut):
    pass


class UsersActivationUserPatchOut(BaseSchema):
    status: bool


class UsersBlockingUserPatchOut(BaseSchema):
    status: bool


class UserListOutSchema(PaginatedListSchema, BaseSchema):
    data: Optional[List[UserDBReadModel]]


class UsersGetUserSubListOut(BaseUserSchema):
    id: SchemaID
    avatar: Optional[str]
    role: RoleEnum
    login_type: Optional[LoginType]
    login_datetime: Optional[datetime]
    country: Optional[CountryCode]
    user_status: Optional[UserStatus]


class UsersGetCustomerSubListOut(UsersGetUserSubListOut):
    login_type: Optional[LoginType]
    login_datetime: Optional[datetime]
    country: Optional[CountryCode]
    is_blocked: bool
    block_info: Optional[BlockInfo]
    business_type: Optional[BusinessTypeEnum]
    nick_name: Optional[str]
    create_datetime: datetime


class UsersChangePasswordByAdminIn(BaseModel):
    new_password: str = Field(min_length=8, max_length=50, example="0123456789")


class UsersUpdateUserIn(UserCreateSchema):
    first_name: Optional[str] = Field(example="John")
    groups: Optional[List[Union[str, CreateUserGroupEnum]]]
    is_blocked: Optional[bool]
    is_force_change_password: Optional[bool]
    last_name: Optional[str] = Field(example="Doe")
    password: Optional[str] = Field(example="0123456789")
    block_reason: Optional[BlockInfoSchemaIn]

    @validator("block_reason", always=True)
    @classmethod
    def validate_block_reason_type(cls, value, values):
        if values.get("is_blocked") is True and not value:
            raise ValueError("enter block_reason")
        return value


class UsersUpdateAdminUserIn(UsersCreateAdminIn):
    first_name: Optional[str] = Field(example="John")
    groups: Optional[List[Union[str, CreateUserGroupEnum]]]
    is_blocked: Optional[bool]
    is_force_change_password: Optional[bool]
    last_name: Optional[str] = Field(example="Doe")
    password: Optional[str] = Field(example="0123456789")
    business_type: Optional[BusinessTypeEnum]
    nick_name: Optional[str]
    block_reason: Optional[BlockInfoSchemaIn]

    @validator("block_reason", always=True)
    @classmethod
    def validate_block_reason_type(cls, value, values):
        if values.get("is_blocked") is True and not value:
            raise ValueError("enter block_reason")
        return value


class UserJoinSchemaOut(BaseSchema):
    id: SchemaID
    first_name: Optional[str] = Field(example="John")
    last_name: Optional[str] = Field(example="Doe")
    email: Optional[OptionalEmailStr] = Field(example="user@fanpino.com")
    mobile_number: Optional[str] = Field(example="+989123456789")
    is_enable: Optional[bool]
    avatar: Optional[str]


class AuditGetUsersListSchema(BaseSchema):
    id: SchemaID
    avatar: Optional[str]
    mobile_number: Optional[str]
    email: Optional[str]
    create_datetime: datetime
    first_name: Optional[str]
    last_name: Optional[str]
    nick_name: Optional[str]


class SubActivityUser(AuditGetUsersListSchema):
    business_type: BusinessTypeEnum


class AuditActivityUserListSchema(BaseSchema):
    user: SubActivityUser
    meta: dict = Field(alias="action_status")
    description: Optional[str]
    create_datetime: datetime


class AuditGetUserDetailSchema(AuditGetUsersListSchema):
    business_type: BusinessTypeEnum
    is_blocked: bool
    block_info: Optional[BlockInfo]


class AuditUpdateUserIn(BaseSchema):
    is_blocked: bool
    block_reason: Optional[BlockInfoSchemaIn]

    @validator("block_reason", always=True)
    @classmethod
    def validate_block_reason_type(cls, value, values):
        if values.get("is_blocked") is True and not value:
            raise ValueError("enter block_reason_type")
        return value


class AddressSchema(BaseSchema):
    first_name: Optional[str]
    last_name: Optional[str]
    country_code: Optional[str]
    phone_number: Optional[str]
    alternate_phone_number: Optional[str]
    location: Optional[PointField]
    street: Optional[str]
    address_line_1: Optional[str]
    address_line_2: Optional[str]
    state: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    is_default: Optional[bool] = False
    type: Optional[AddressType]
    landmark: Optional[str]
    address_name: Optional[str]
    building_name: Optional[str]
    area: Optional[str]
    town: Optional[str]
    apartment_number: Optional[str]


class AddressSchemaUpdateIn(BaseSchema):
    first_name: Optional[str]
    last_name: Optional[str]
    country_code: Optional[str]
    phone_number: Optional[str]
    alternate_phone_number: Optional[str]
    location: Optional[PointField]
    street: Optional[str]
    address_line_1: Optional[str]
    address_line_2: Optional[str]
    state: Optional[str]
    city: Optional[str]
    postal_code: Optional[str]
    is_default: Optional[bool] = False
    type: Optional[AddressType]
    landmark: Optional[str]
    address_name: Optional[str]
    building_name: Optional[str]
    area: Optional[str]
    town: Optional[str]
    apartment_number: Optional[str]


class ProfileUpdateMeIn(BaseSchema):
    avatar: Optional[HttpUrl]
    date_of_birth: Optional[date] = Field(example="1999-09-09")
    first_name: Optional[str]
    gender: Optional[GenderEnum] = Field(example=GenderEnum.male)
    last_name: Optional[str]
    mobile_number: Optional[str] = Field(example="+982112345678")
    national_code: Optional[str]
    settings: Optional[UserSettings]
    telephone: Optional[str]

    @validator("mobile_number")
    @classmethod
    def validate_mobile_number(cls, value: str):
        if not value:
            return value
        try:
            mobile_number_obj = phonenumbers.parse(value, "UAE")
            return phonenumbers.format_number(
                mobile_number_obj,
                phonenumbers.PhoneNumberFormat.E164,
            )
        except phonenumbers.NumberParseException as e:
            raise ValueError("Invalid Phone Number") from e


class ProfileGetMeOut(BaseSchema):
    id: SchemaID
    first_name: Optional[str] = Field(example="John")
    last_name: Optional[str] = Field(example="Doe")
    date_of_birth: Optional[date] = Field(example="1999-09-09")
    gender: Optional[GenderEnum] = Field(example=GenderEnum.male)
    is_force_change_password: Optional[bool] = Field(example=True)
    is_force_login: Optional[bool] = Field(example=False)
    is_enable: Optional[bool]
    login_datetime: Optional[datetime]
    last_login_datetime: Optional[datetime]
    email: Optional[OptionalEmailStr] = Field(example="user@fanpino.com")
    mobile_number: Optional[str] = Field(example="+989123456789")
    national_code: Optional[str] = Field(example="0123456789")
    addresses: Optional[List[AddressSchemaOut]]
    role: Optional[RoleEnum] = Field(example=RoleEnum.admin)
    avatar: Optional[str]
    settings: UserSettings
    telephone: Optional[str]
    user_status: UserStatus
    login_type: Optional[LoginType]
    create_datetime: datetime
    phone_verified: Optional[bool]
    email_verified: Optional[bool]
    user_type: Optional[UserType]
    business_type: Optional[BusinessTypeEnum]
    nick_name: Optional[str]


class ProfileUpdateMeOut(ProfileGetMeOut):
    pass


class CustomerProfileUpdateMeIn(BaseSchema):
    avatar: Optional[HttpUrl]
    date_of_birth: Optional[date] = Field(example="1999-09-09")
    first_name: Optional[str]
    last_name: Optional[str]
    settings: Optional[UserSettings]
    business_type: Optional[BusinessTypeEnum]
    nick_name: Optional[str]


class AuditProfileUpdateMeIn(BaseSchema):
    avatar: Optional[HttpUrl]
    date_of_birth: Optional[date] = Field(example="1999-09-09")
    first_name: Optional[str]
    last_name: Optional[str]
    settings: Optional[UserSettings]


class UserBulkUpdateIn(UsersUpdateUserIn):
    ids: List[SchemaID]


class AddNewDeviceIn(BaseSchema):
    notification_token: str
    device_type: Optional[DeviceType]
    notification_enabled: bool = True


class BankCardOut(BaseSchema):
    id: SchemaID
    scheme: str
    maskedPan: str
    cvv: Optional[str]
    recaptureCsc: Optional[bool] = True
    expiry: Optional[str]
    cardholderName: Optional[str]
    is_enable: Optional[bool]


class ProfileGetPermssions(BaseSchema):
    permissions: Optional[List[Optional[PermissionModel]]]


class ProfileGetPermssionsDict(BaseSchema):
    permissions: Dict[str, List[str]]
