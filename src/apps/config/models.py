from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from bson import Decimal128
from pydantic import BaseModel, Field, validator, EmailStr

from src.apps.config.common_model import OfficeAddress
from src.core import mixins
from src.core.base.models import BaseDBReadModel, BaseDBModel
from src.core.mixins import UpdateDatetimeMixin, DB_ID, default_id
from src.main.config import collections_names


class ShippingConditionCreateModel(BaseModel):
    min_order_total_amount: Optional[Decimal128] = Decimal128("100")
    shipping_amount: Optional[Decimal128] = Decimal128("0")

    class Config(BaseModel.Config):
        arbitrary_types_allowed = True

    # pylint: disable=no-self-argument,no-self-use
    @validator("shipping_amount", "min_order_total_amount", pre=True)
    def create_decimals(cls, value: Optional[Decimal]):
        return Decimal128(str(value or 0))


class ShippingConditionReadModel(BaseModel):
    min_order_total_amount: Optional[Decimal]
    shipping_amount: Optional[Decimal]

    class Config(BaseModel.Config):
        arbitrary_types_allowed = True

    # pylint: disable=no-self-argument,no-self-use
    @validator("shipping_amount", "min_order_total_amount", pre=True)
    def read_decimals(cls, value):
        return value.to_decimal() if value and isinstance(value, Decimal128) else value


class GuestCouponModel(BaseModel):
    discount_percentage: float
    discount_amount: float
    max_quantity: float
    total_generated: float
    end_datetime: datetime
    is_enable: Optional[bool] = True


class ConfigBaseModel(
    mixins.SoftDeleteMixin,
    mixins.IsEnableMixin,
    BaseDBModel,
):
    auto_confirmation: Optional[bool]
    offer_icon: Optional[str]
    shipping_min_time_minutes: Optional[int]
    shipping_max_time_minutes: Optional[int]
    vat_rate: Optional[float] = Field(0, gte=0, lte=1)
    office_address: Optional[OfficeAddress]
    default_min_stock_quantity: Optional[int]
    other_configs: Optional[dict]
    default_email_recipients: Optional[List[EmailStr]]

    class Config(BaseModel.Config):
        arbitrary_types_allowed = True

    class Meta:
        collection_name = collections_names.CONFIGS
        entity_name = "config"


class ConfigDBReadModel(ConfigBaseModel, BaseDBReadModel):
    id: DB_ID
    shipping_guarantee: Decimal
    express_shipping_cost: Decimal

    is_enable: bool
    is_deleted: bool

    # pylint: disable=no-self-argument,no-self-use
    @validator("shipping_guarantee", "express_shipping_cost", pre=True)
    def read_decimals(cls, value):
        return value.to_decimal() if value and isinstance(value, Decimal128) else value


class ConfigDBCreateModel(ConfigBaseModel, mixins.CreateDatetimeMixin):
    id: DB_ID = Field(default_factory=default_id)
    shipping_guarantee: Optional[Decimal128] = Decimal128("0")
    express_shipping_cost: Optional[Decimal128] = Decimal128("0")
    other_configs: Optional[dict] = {}
    default_min_stock_quantity: Optional[int] = 1
    default_email_recipients: Optional[List[EmailStr]] = []
    is_enable: bool
    is_deleted: bool

    # pylint: disable=no-self-argument,no-self-use
    @validator("shipping_guarantee", "express_shipping_cost", pre=True)
    def create_decimals(cls, value: Optional[Decimal]):
        return Decimal128(str(value or 0))


class ConfigDBUpdateModel(ConfigBaseModel, UpdateDatetimeMixin):
    is_enable: Optional[bool]
    is_deleted: Optional[bool]
    shipping_guarantee: Optional[Decimal128]
    express_shipping_cost: Optional[Decimal128]

    # pylint: disable=no-self-argument,no-self-use
    @validator("shipping_guarantee", "express_shipping_cost", pre=True)
    def create_decimals(cls, value: Optional[Decimal]):
        return Decimal128(str(value or 0))
