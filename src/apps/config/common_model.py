from typing import Optional

from pydantic import BaseModel

from src.apps.user.enum import AddressType
from src.core.mixins.fields import PointField


class OfficeAddress(BaseModel):
    address_id: Optional[str] = "keywords_project"
    address_line_1: Optional[str] = "keywords project"
    address_line_2: Optional[str] = "keywords project"
    address_name: Optional[str] = " keywords projectAddress"
    alternate_phone_number: Optional[str] = "+971123456879"
    apartment_number: Optional[str] = "apartment_number"
    area: Optional[str] = "Dubai"
    building_name: Optional[str] = "keywords"
    city: Optional[str] = "Dubai"
    country_code: Optional[str] = "UAE"
    first_name: Optional[str] = "keywords project"
    landmark: Optional[str] = "landmark"
    last_name: Optional[str] = "keywords"
    location: Optional[PointField] = {"coordinates": [25.1, 55.17], "type": "Point"}
    phone_number: Optional[str] = "+971123456879"
    postal_code: Optional[str] = "postal_code"
    state: Optional[str] = "Dubai"
    street: Optional[str] = "street"
    town: Optional[str] = "town"
    type: Optional[AddressType] = AddressType.warehouse
