from datetime import datetime
from typing import Optional

from src.apps.log_app.enum import LogActionEnum
from src.apps.user.models import UserDBReadModel
from src.core.base.schema import BaseSchema
from src.core.mixins import SchemaID


class LogBaseSchema(BaseSchema):
    action: LogActionEnum
    action_by: SchemaID
    entity: str
    entity_id: Optional[SchemaID]
    meta: dict
    description: Optional[str]


class LogGetListSchema(LogBaseSchema):
    id: SchemaID
    action_by: UserDBReadModel
    meta: Optional[dict]
    entity: str
    is_enable: bool
    create_datetime: datetime


class LogGetOut(LogBaseSchema):
    id: SchemaID
    action_by: UserDBReadModel
    meta: Optional[dict]
    entity_obj: Optional[dict]
    is_enable: bool
    create_datetime: datetime
