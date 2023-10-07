import abc
import random
import string
import uuid
from enum import Enum
from typing import Optional, Union
import phonenumbers
from bson import ObjectId
from src.core.utils import phone_to_e164_format
from pydantic import BaseModel, EmailStr, Field, validate_email
from bson import Decimal128

__all__ = ("DB_ID", "SchemaID", "default_id", "OptionalEmailStr", "DimensionsField")

DB_ID = str
SchemaID = str


# we do the following for lazy initialization
# just a tiny hack to make the tests & patches work


def default_id():
    return str(uuid.uuid4())  # noqa: E731


def random_code():
    return "".join(
        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
        for _ in range(6)
    )


def get_random_gift_key():
    return "".join(
        random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase)
        for _ in range(16)
    )


class CustomUUID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


class OptionalEmailStr(EmailStr):
    @classmethod
    def validate(cls, value: Optional[str]) -> Optional[str]:
        return None if not value or value == "none" else validate_email(value)[1]


NumType = Union[float, int]
# Coordinate = Union[Tuple[NumType, NumType], Tuple[NumType, NumType, NumType]]
Coordinate = list  # TODO Fix This


class _GeometryBase(BaseModel, abc.ABC):
    """Base class for geometry models"""

    coordinates: Coordinate

    @property
    def __geo_interface__(self):
        return self.dict()


class CoordinateType(str, Enum):
    point = "Point"


class PointField(_GeometryBase):
    """Point Model"""

    type: CoordinateType = Field(CoordinateType.point.value, const=True)
    coordinates: Coordinate


class DimensionsField(BaseModel):
    length: float
    width: float
    height: float


# class DimensionsFieldSchema(BaseModel):
#     length: Decimal
#     width: Decimal
#     height: Decimal


class PhoneStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        try:
            if value.startswith("00"):
                value = value.replace("00", "+", 1)
            return phone_to_e164_format(value)
        except phonenumbers.NumberParseException as e:
            raise ValueError("Invalid Phone Number") from e

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            type="string",
            example="+989123456789",
        )


class PyDecimal128(Decimal128):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        return Decimal128(str(value))

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            type="number",
            example="11.5",
        )


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")
