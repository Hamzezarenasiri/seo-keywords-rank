from typing import List, Optional, Union

from fastapi.security import SecurityScopes

from src.apps.auth.exception import PermissionDenied
from src.apps.auth.models import (
    EntityDBCreateModel,
    EntityDBReadModel,
    EntityDBUpdateModel,
    GroupDBCreateModel,
    GroupDBReadModel,
    GroupDBUpdateModel,
)
from src.apps.user.enum import DefaultGroupNameEnum
from src.apps.user.models import UserDBReadModel
from src.core.base.crud import BaseCRUD


class GroupCRUD(BaseCRUD):
    async def get_list_by_names(
        self,
        names: Optional[List[Union[str, DefaultGroupNameEnum]]],
        skip: int = 0,
        limit: int = 0,
        sort: Optional[list] = None,
        deleted: Optional[bool] = False,
    ) -> Optional[List[GroupDBReadModel]]:
        if not names:
            return None
        return await self.get_list(
            criteria={"name": {"$in": names}},
            skip=skip,
            limit=limit,
            sort=sort,
            deleted=deleted,
        )


class EntityCRUD(BaseCRUD):
    async def get_entity_rules(self, code_name: str) -> List[str]:
        entities = await self.get_object(criteria={"code_name": code_name})
        return entities.rules

    async def get_all_entities_name(self) -> List[str]:
        permissions = await self.get_list()
        return [entity.code_name for entity in permissions]


class PermissionCRUD(object):
    async def get_permissions_dict(self, user_obj: UserDBReadModel) -> dict:
        groups = await groups_crud.get_list_by_names(names=user_obj.groups) or []
        permissions = {
            permission.entity: permission.rules
            for permission in user_obj.permissions or []
        }
        for group in groups:
            for permission in group.permissions:
                if permissions.get(permission.entity):
                    permissions[permission.entity] = list(
                        set(permission.rules + permissions[permission.entity])
                    )
                permissions[permission.entity] = permission.rules
        return permissions

    async def check_permissions(
        self, security_scopes: SecurityScopes, user_obj: UserDBReadModel
    ) -> UserDBReadModel:
        if not security_scopes.scopes:
            return user_obj
        entity_scope, rule = security_scopes.scopes
        permissions = await self.get_permissions_dict(user_obj)
        if entity_scope in permissions and rule in permissions[entity_scope]:
            return user_obj
        else:
            raise PermissionDenied


entities_crud = EntityCRUD(
    read_db_model=EntityDBReadModel,
    create_db_model=EntityDBCreateModel,
    update_db_model=EntityDBUpdateModel,
)

groups_crud = GroupCRUD(
    read_db_model=GroupDBReadModel,
    create_db_model=GroupDBCreateModel,
    update_db_model=GroupDBUpdateModel,
)

permissions_crud = PermissionCRUD()
