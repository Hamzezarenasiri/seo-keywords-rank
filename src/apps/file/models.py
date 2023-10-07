from typing import List, Optional

from pydantic import Field

from src.apps.file.enum import FileTypeEnum
from src.core import mixins
from src.core.base.models import BaseDBReadModel, BaseDBModel
from src.core.mixins import DB_ID, UpdateDatetimeMixin, default_id
from src.core.mixins.fields import SchemaID
from src.main.config import collections_names


class FileBaseModel(
    mixins.SoftDeleteMixin,
    mixins.IsEnableMixin,
    BaseDBModel,
):
    alt: Optional[str]
    user_id: DB_ID
    file_url: str
    thumbnail_url: Optional[str]
    file_type: FileTypeEnum
    # file_category: Optional[FileCategoryEnum]
    file_name: str = Field(max_length=100)
    is_used: bool = Field(
        default=False, description="True is file has been used in other documents."
    )
    entity_ids: Optional[List[SchemaID]]

    class Meta:
        collection_name = collections_names.FILES
        entity_name = "file"


class FileDBReadModel(FileBaseModel, BaseDBReadModel):
    id: DB_ID
    is_enable: bool
    is_deleted: bool


class FileDBCreateModel(
    FileBaseModel,
    mixins.CreateDatetimeMixin,
):
    id: DB_ID = Field(default_factory=default_id)
    alt: Optional[str]
    # file_category: Optional[FileCategoryEnum] = FileCategoryEnum.gallery


class FileDBUpdateModel(FileBaseModel, UpdateDatetimeMixin):
    is_enable: Optional[bool]
    is_deleted: Optional[bool]
    alt: Optional[str]
    file_name: Optional[str] = Field(max_length=100)
    file_url: Optional[str]
