from typing import Optional, List
from src.core.base.schema import BaseSchema
from src.core.mixins import SchemaID
from src.core.mixins.fields import PointField


class StateListSchema(BaseSchema):
    id: SchemaID
    name: str
    is_enable: bool


class StateDetailSchema(BaseSchema):
    id: SchemaID
    name: str
    is_enable: bool


class StateCreateIn(BaseSchema):
    name: str
    default_location: Optional[PointField]
    is_enable: Optional[bool]


class StateUpdateIn(BaseSchema):
    name: Optional[str]
    default_location: Optional[PointField]
    is_enable: Optional[bool]


class CityListSchema(BaseSchema):
    id: SchemaID
    name: str
    neighbourhoods: Optional[List[str]]
    default_location: Optional[PointField]
    state_id: SchemaID
    is_enable: bool


class CityDetailSchema(BaseSchema):
    id: SchemaID
    name: str
    default_location: Optional[PointField]
    neighbourhoods: Optional[List[str]]
    state_id: SchemaID
    is_enable: bool


class CityCreateIn(BaseSchema):
    name: str
    default_location: Optional[PointField]
    neighbourhoods: Optional[List[str]]
    state_id: SchemaID
    is_enable: Optional[bool]


class CityUpdateIn(BaseSchema):
    name: Optional[str]
    default_location: Optional[PointField]
    neighbourhoods: Optional[List[str]]
    is_enable: Optional[bool]
