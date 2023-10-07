from typing import Optional

from ..base.schema import BaseSchema
from .fields import PhoneStr


class MobileNumberSchemaMixin(BaseSchema):
    mobile_number: Optional[PhoneStr]
