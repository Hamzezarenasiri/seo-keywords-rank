from typing import List, Optional, Union

import pymongo
from pydantic import BaseModel

from src.apps.user.enum import DefaultGroupNameEnum
from src.core import mixins
from src.core.base.models import BaseDBReadModel, BaseDBModel
from src.core.mixins import UpdateDatetimeMixin
from src.main.config import collections_names


class PermissionModel(BaseModel):
    entity: str
    rules: List[str]


class GroupBaseModel(
    mixins.SoftDeleteMixin,
    mixins.IsEnableMixin,
    BaseDBModel,
):
    name: Union[str, DefaultGroupNameEnum]
    permissions: Optional[List[Optional[PermissionModel]]]

    class Config(BaseModel.Config):
        arbitrary_types_allowed = True

    class Meta:
        collection_name = collections_names.GROUPS
        entity_name = "group"
        indexes = [
            pymongo.IndexModel("name", name="group_name"),
        ]


class GroupDBReadModel(GroupBaseModel, BaseDBReadModel):
    is_enable: bool
    is_deleted: bool


class GroupDBCreateModel(
    GroupBaseModel,
    mixins.CreateDatetimeMixin,
):
    pass


class GroupDBUpdateModel(GroupBaseModel, UpdateDatetimeMixin):
    is_enable: Optional[bool]
    is_deleted: Optional[bool]
    name: Optional[str]


class EntityBaseModel(
    mixins.SoftDeleteMixin,
    mixins.IsEnableMixin,
    BaseDBModel,
):
    code_name: str
    rules: List[str]
    description: Optional[str]

    class Meta:
        collection_name = collections_names.ENTITIES
        entity_name = "entity"
        indexes = [
            pymongo.IndexModel("code_name", name="code_name"),
        ]


class EntityDBReadModel(EntityBaseModel, BaseDBReadModel):
    is_enable: bool
    is_deleted: bool


class EntityDBCreateModel(
    EntityBaseModel,
    mixins.CreateDatetimeMixin,
):
    pass


class EntityDBUpdateModel(EntityBaseModel, UpdateDatetimeMixin):
    is_enable: Optional[bool]
    is_deleted: Optional[bool]
    code_name: Optional[str]
    rules: Optional[List[str]]


class RuleBaseModel(
    mixins.SoftDeleteMixin,
    mixins.IsEnableMixin,
    BaseDBModel,
):
    code_name: str
    description: str

    class Meta:
        collection_name = collections_names.RULES
        entity_name = "rule"
        indexes = [
            pymongo.IndexModel("code_name", name="code_name", unique=True),
        ]


class RuleDBReadModel(RuleBaseModel, BaseDBReadModel):
    is_enable: bool
    is_deleted: bool


class RuleDBCreateModel(
    RuleBaseModel,
    mixins.CreateDatetimeMixin,
):
    pass


class RuleDBUpdateModel(RuleBaseModel, UpdateDatetimeMixin):
    is_enable: Optional[bool]
    is_deleted: Optional[bool]
    code_name: Optional[str]
    description: Optional[str]
