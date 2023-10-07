from decimal import Decimal
from typing import Optional, List

from pydantic import Field, EmailStr

from src.apps.config.common_model import OfficeAddress
from src.core.base.schema import BaseSchema


class ShippingConditionReadSchema(BaseSchema):
    min_order_total_amount: Optional[Decimal]
    shipping_amount: Optional[Decimal]


class ConfigBaseSchema(BaseSchema):
    auto_confirmation: Optional[bool]
    default_min_stock_quantity: Optional[int]
    shipping_guarantee: Optional[Decimal]
    express_shipping_cost: Optional[Decimal]
    offer_icon: Optional[str]
    shipping_min_time_minutes: Optional[int]
    shipping_max_time_minutes: Optional[int]
    vat_rate: Optional[float] = Field(0, gte=0, lte=1)
    office_address: Optional[OfficeAddress]
    is_enable: Optional[bool]
    other_configs: Optional[dict]
    default_email_recipients: Optional[List[EmailStr]] = []


class ConfigGetOut(ConfigBaseSchema):
    pass


class ConfigUpdateIn(ConfigBaseSchema):
    pass


class ConfigUpdateOut(ConfigGetOut):
    pass
