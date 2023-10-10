from datetime import datetime
from typing import Optional

import pymongo
from pydantic import BaseModel, Field

from src.core import mixins
from src.core.base.models import BaseDBReadModel, BaseDBModel
from src.core.mixins import DB_ID, default_id
from src.main.config import collections_names


class RelatedKeywordModel(BaseModel):
    keyword_id: DB_ID
    flavor: Optional[str]
    title: Optional[str]


class KeywordBaseModel(
    BaseDBModel,
    mixins.IsEnableMixin,
    mixins.SoftDeleteMixin,
):
    keyword: str
    domain: str
    rank: None | int
    last_rank_update_time: None | datetime

    class Config(BaseModel.Config):
        arbitrary_types_allowed = True

    class Meta:
        collection_name = collections_names.KEYWORDS
        entity_name = "keyword"
        indexes = [pymongo.IndexModel("id", name="id", unique=True)]


class KeywordDBReadModel(KeywordBaseModel, BaseDBReadModel):
    id: DB_ID
    is_deleted: bool
    is_enable: bool

    pass


class KeywordDBCreateModel(KeywordBaseModel, mixins.CreateDatetimeMixin):
    id: DB_ID = Field(default_factory=default_id)
    pass


class KeywordDBUpdateModel(KeywordBaseModel, mixins.UpdateDatetimeMixin):
    pass
