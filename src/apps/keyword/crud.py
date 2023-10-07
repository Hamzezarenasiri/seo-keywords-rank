from decimal import Decimal
from typing import Optional, TypeVar, List

import pymongo
from bson import Decimal128

from src.apps.language.enum import LanguageEnum
from src.apps.keyword.exception import KeywordNotFound
from src.apps.keyword.models import (
    KeywordDBCreateModel,
    KeywordDBReadModel,
    KeywordDBUpdateModel,
)
from src.core.base.crud import BaseCRUD
from src.core.base.schema import BaseSchema
from src.core.helpers.datetime_helper import datetime_helper
from src.core.mixins import DB_ID, SchemaID
from src.main.config import collections_names, app_settings
from src.services.db.mongodb import UpdateOperatorsEnum

T = TypeVar("T", bound=BaseSchema)


class KeywordCRUD(BaseCRUD):
    pass


keywords_crud = KeywordCRUD(
    read_db_model=KeywordDBReadModel,
    create_db_model=KeywordDBCreateModel,
    update_db_model=KeywordDBUpdateModel,
)
