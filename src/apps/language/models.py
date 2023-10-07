from typing import Dict, Optional

from src.apps.language.enum import LanguageEnum, LocaleEnum
from src.core import mixins
from src.core.base.models import BaseDBReadModel, BaseDBModel
from src.core.mixins import UpdateDatetimeMixin
from src.main.config import collections_names


class LanguageBaseModel(
    mixins.SoftDeleteMixin,
    mixins.IsEnableMixin,
    BaseDBModel,
):
    name: str
    icon: Optional[str]
    direction: Optional[str]
    is_default: bool = False
    messages: Optional[Dict[str, str]]

    class Meta:
        collection_name = collections_names.LANGUAGES
        entity_name = "language"


class LanguageDBReadModel(LanguageBaseModel, BaseDBReadModel):
    code: LanguageEnum
    locale: LocaleEnum
    is_enable: bool
    is_deleted: bool


class LanguageDBCreateModel(
    LanguageBaseModel,
    mixins.CreateDatetimeMixin,
):
    code: LanguageEnum
    locale: LocaleEnum


class LanguageDBUpdateModel(LanguageBaseModel, UpdateDatetimeMixin):
    is_enable: Optional[bool]
    is_deleted: Optional[bool]
    name: Optional[str]
    is_default: Optional[bool]
