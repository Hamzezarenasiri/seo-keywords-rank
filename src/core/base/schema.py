from datetime import datetime, time
from typing import Generic, List, Optional, TypeVar, Union

from bson import Decimal128, ObjectId
from pydantic import (
    AnyHttpUrl,
    BaseConfig as PydanticBaseConfig,
    BaseModel as PydanticBaseModel,
)
from pydantic.generics import GenericModel

from src.core.mixins import SchemaID
from src.main.config import app_settings


class BaseConfig(PydanticBaseConfig):
    allow_population_by_field_name = True
    anystr_strip_whitespace = True
    max_anystr_length = app_settings.DEFAULT_MAX_STR_LENGTH
    arbitrary_types_allowed = True
    use_enum_values = True
    json_encoders = {
        SchemaID: str,
        # time: lambda t: t.isoformat(),
        time: lambda t: t.strftime("%H:%M:%S.%fZ"),
        # datetime: lambda dt: dt.isoformat(),
        ObjectId: str,
        datetime: lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        Decimal128: lambda d: d.to_decimal(),
    }


class BaseSchema(PydanticBaseModel):
    class Config(BaseConfig):
        pass


DataT = TypeVar("DataT", bound=PydanticBaseModel)
MessageT = TypeVar("MessageT")
DetailT = TypeVar("DetailT")


class Response(GenericModel, Generic[DataT]):
    data: Optional[DataT] = {}
    success: bool = True
    message: Optional[str] = "Ok"
    detail: Optional[Union[str, List]] = []

    class Config(BaseConfig):
        pass


class ErrorResponse(GenericModel, Generic[MessageT]):
    data: Optional[dict] = {}
    success: bool = False
    message: Optional[MessageT] = "Error"
    detail: Optional[Union[str, List]] = []


ListDataT = TypeVar("ListDataT", bound=list)


class PaginatedResponse(GenericModel, Generic[ListDataT]):
    total: Optional[int]
    offset: Optional[int]
    limit: Optional[int]
    next: Optional[AnyHttpUrl]
    previous: Optional[AnyHttpUrl]
    result: Optional[ListDataT] = []

    class Config(BaseConfig):
        pass


class PaginatedListSchema(BaseSchema):
    count: Optional[int]
    offset: Optional[int]
    limit: Optional[int]
    next: Optional[str]
    previous: Optional[str]
    data: Optional[list]


class BulkDeleteIn(BaseSchema):
    ids: List[SchemaID]


class CommonExportCsvSchemaOut(BaseSchema):
    url: str


class CursorPaginatedResponse(GenericModel, Generic[ListDataT]):
    total: Optional[int] = 0
    next_cursor: Optional[str]
    previous_cursor: Optional[str]
    result: Optional[ListDataT] = []

    class Config(BaseConfig):
        pass
