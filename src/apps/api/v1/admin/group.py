from typing import List

from fastapi import APIRouter, Depends, Path, Security, status, BackgroundTasks
from starlette.responses import Response as StarletteResponse

from src.apps.auth import schema as group_schema
from src.apps.auth.controller import group_controller
from src.apps.auth.deps import get_admin_user
from src.apps.auth.enum import GroupMessageEnum
from src.apps.log_app.controller import log_controller
from src.apps.log_app.enum import LogActionEnum
from src.apps.user.models import UserDBReadModel
from src.core.base.schema import Response, PaginatedResponse, BulkDeleteIn
from src.core.mixins import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses, response_404
from src.core.utils import return_on_failure
from src.main.config import collections_names

group_router = APIRouter()
entity = collections_names.GROUPS


@group_router.post(
    "",
    status_code=201,
    responses={**common_responses},
    response_model=Response[group_schema.GroupCreateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def create_new_group(
    background_tasks: BackgroundTasks,
    payload: group_schema.GroupCreateIn,
    current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "create"]),
):
    result_data = await group_controller.create_new_group(
        new_group_data=payload,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.insert,
        action_by=current_user.id,
        entity=entity,
        entity_id=result_data.name,
    )
    return Response[group_schema.GroupCreateOut](
        data=result_data, message=GroupMessageEnum.create_new_group
    )


@group_router.get(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[PaginatedResponse[List[group_schema.GroupGetListOut]]],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_all_group(
    _: UserDBReadModel = Security(get_admin_user, scopes=[entity, "list"]),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    result_data = await group_controller.get_all_group(
        pagination=pagination, ordering=ordering
    )
    return Response[PaginatedResponse[List[group_schema.GroupGetListOut]]](
        data=result_data.dict(), message=GroupMessageEnum.get_groups
    )


@group_router.get(
    "/{group_name}/",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[group_schema.GroupGetOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_single_group(
    group_name: SchemaID = Path(...),
    _: UserDBReadModel = Security(get_admin_user, scopes=[entity, "read"]),
):
    result_data = await group_controller.get_single_group(target_group_name=group_name)
    return Response[group_schema.GroupGetOut](
        data=result_data, message=GroupMessageEnum.get_single_group
    )


@group_router.patch(
    "/{group_name}/",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[group_schema.GroupUpdateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def update_single_group(
    background_tasks: BackgroundTasks,
    payload: group_schema.GroupUpdateIn,
    group_name: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "update"]),
):
    result_data = await group_controller.update_single_group(
        target_group_name=group_name,
        new_group_data=payload,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=group_name,
    )
    return Response[group_schema.GroupUpdateOut](
        data=result_data, message=GroupMessageEnum.update_group
    )


@group_router.delete(
    "/{group_name}/",
    status_code=204,
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def delete_single_group(
    background_tasks: BackgroundTasks,
    group_name: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "delete"]),
):
    if await group_controller.soft_delete_single_group(
        name=group_name,
    ):
        background_tasks.add_task(
            func=log_controller.create_log,
            action=LogActionEnum.delete,
            action_by=current_user.id,
            entity=entity,
            entity_id=group_name,
        )
        return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)


@group_router.delete(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def bulk_delete_groups(
    background_tasks: BackgroundTasks,
    payload: BulkDeleteIn,
    current_user: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "delete"],
    ),
):
    await group_controller.bulk_delete_groups(
        obj_ids=payload.ids,
    )
    background_tasks.add_task(
        func=log_controller.bulk_create_log,
        action=LogActionEnum.delete,
        action_by=current_user.id,
        entity=entity,
        entity_ids=payload.ids,
    )
    return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)
