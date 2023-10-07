import pymongo
from typing import Optional
from pydantic import BaseModel, Field

from src.apps.log_app.enum import LogActionEnum
from src.core import mixins
from src.core.base.models import BaseDBReadModel, BaseDBModel
from src.core.mixins import DB_ID, default_id
from src.main.config import collections_names


class LogBaseModel(
    mixins.SoftDeleteMixin,
    mixins.IsEnableMixin,
    BaseDBModel,
):
    action: LogActionEnum
    action_by: DB_ID
    entity: str
    entity_id: Optional[DB_ID]
    meta: Optional[dict]
    description: Optional[str]

    class Meta:
        collection_name = collections_names.LOGS
        entity_name = "log"
        indexes = [
            pymongo.IndexModel("action_by", name="action_by"),
        ]


class LogDBReadModel(LogBaseModel, BaseDBReadModel):
    id: DB_ID
    is_enable: bool
    is_deleted: bool


class LogDBCreateModel(
    LogBaseModel,
    mixins.CreateDatetimeMixin,
):
    id: DB_ID = Field(default_factory=default_id)


class LogDBUpdateModel(LogBaseModel):
    pass


class ProductImportLogMetaModel(BaseModel):
    failed: Optional[dict]
    inserted: Optional[int]
    error: Optional[str]
