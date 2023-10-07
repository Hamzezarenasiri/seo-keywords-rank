from typing import List
from fastapi import (
    APIRouter,
    BackgroundTasks,
    responses,
    Security,
    Depends,
    Path,
)
from src.main.config import collections_names
from src.core.utils import return_on_failure
from src.core.mixins import SchemaID
from src.core.responses import common_responses, response_404
from src.core.base.schema import Response, PaginatedResponse
from src.core.pagination import Pagination
from src.core.ordering import Ordering
from src.apps.auth.deps import get_admin_user
from src.apps.log_app.controller import log_controller
from src.apps.log_app.enum import LogActionEnum
from src.apps.user.models import UserDBReadModel
from src.apps.country import schema as state_schemas
from src.apps.country.controller import state_controller

entity = collections_names.STATES
router = APIRouter()


@router.get(
    "",
    responses={**common_responses},
    response_model=Response[PaginatedResponse[List[state_schemas.StateListSchema]]],
    description="by `HamzeZN`",
)
@return_on_failure
async def admin_get_states(
    current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "list"]),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    criteria = {"is_deleted": False}
    states = await state_controller.get_list_objs(
        pagination=pagination,
        ordering=ordering,
        criteria=criteria,
        sub_list_schema=state_schemas.StateListSchema,
    )
    return Response[PaginatedResponse[List[state_schemas.StateListSchema]]](data=states)


@router.post(
    "",
    responses={**common_responses},
    response_model=Response[state_schemas.StateDetailSchema],
    status_code=201,
    description="by `HamzeZN`",
)
@return_on_failure
async def admin_create_state(
    payload: state_schemas.StateCreateIn,
    background_tasks: BackgroundTasks,
    current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "create"]),
):
    state = await state_controller.create_new_obj(new_data=payload)
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.insert,
        action_by=current_user.id,
        entity=entity,
        entity_id=state.id,
    )
    return Response[state_schemas.StateDetailSchema](data=state)


@router.get(
    "/{state_id}",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[state_schemas.StateDetailSchema],
    description="by `HamzeZN`",
)
@return_on_failure
async def admin_get_state(
    state_id: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "read"]),
):
    state = await state_controller.get_single_state(state_id=state_id)
    return Response[state_schemas.StateDetailSchema](data=state)


@router.patch(
    "/{state_id}",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[state_schemas.StateDetailSchema],
    description="by `HamzeZN`",
)
@return_on_failure
async def admin_update_state(
    payload: state_schemas.StateUpdateIn,
    background_tasks: BackgroundTasks,
    state_id: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "update"]),
):
    updated_state = await state_controller.update_single_obj(
        criteria={"id": state_id}, new_data=payload
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=updated_state.id,
    )
    return Response[state_schemas.StateDetailSchema](data=updated_state)


@router.delete(
    "/{state_id}",
    responses={
        **common_responses,
        **response_404,
    },
    description="by `HamzeZN`",
    status_code=204,
)
@return_on_failure
async def admin_delete_state(
    background_tasks: BackgroundTasks,
    state_id: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "list"]),
):
    state_id, city_ids = await state_controller.soft_delete_state(state_id=state_id)
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.delete,
        action_by=current_user.id,
        entity=entity,
        entity_id=state_id,
    )
    if city_ids:
        background_tasks.add_task(
            func=log_controller.bulk_create_log,
            action=LogActionEnum.delete,
            action_by=current_user.id,
            entity=entity,
            entity_ids=city_ids,
        )
    return responses.Response(status_code=204)
