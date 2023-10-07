from typing import Optional, List
from fastapi import (
    APIRouter,
    BackgroundTasks,
    responses,
    Security,
    Depends,
    Path,
    Query,
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
from src.apps.country import schema as city_schemas
from src.apps.country.controller import city_controller

entity = collections_names.CITIES
router = APIRouter()


@router.get(
    "",
    responses={**common_responses},
    response_model=Response[PaginatedResponse[List[city_schemas.CityListSchema]]],
    description="by `HamzeZN`",
)
@return_on_failure
async def admin_get_cities(
    current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "list"]),
    state_id: Optional[SchemaID] = Query(None),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    criteria = {"is_deleted": False}
    if state_id:
        criteria["state_id"] = state_id
    cities = await city_controller.get_list_objs(
        pagination=pagination,
        ordering=ordering,
        criteria=criteria,
        sub_list_schema=city_schemas.CityListSchema,
    )
    return Response[PaginatedResponse[List[city_schemas.CityListSchema]]](data=cities)


@router.post(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[city_schemas.CityDetailSchema],
    status_code=201,
    description="by `HamzeZN`",
)
@return_on_failure
async def admin_create_city(
    payload: city_schemas.CityCreateIn,
    background_tasks: BackgroundTasks,
    current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "create"]),
):
    city = await city_controller.create_city(payload=payload)
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.insert,
        action_by=current_user.id,
        entity=entity,
        entity_id=city.id,
    )
    return Response[city_schemas.CityDetailSchema](data=city)


@router.get(
    "/{city_id}",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[city_schemas.CityDetailSchema],
    description="by `HamzeZN`",
)
@return_on_failure
async def admin_get_city(
    city_id: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "read"]),
):
    city = await city_controller.get_single_city(city_id=city_id)
    return Response[city_schemas.CityDetailSchema](data=city)


@router.patch(
    "/{city_id}",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[city_schemas.CityDetailSchema],
    description="by `HamzeZN`",
)
@return_on_failure
async def admin_update_city(
    payload: city_schemas.CityUpdateIn,
    background_tasks: BackgroundTasks,
    city_id: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "update"]),
):
    updated_city = await city_controller.update_single_obj(
        criteria={"id": city_id}, new_data=payload
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=updated_city.id,
    )
    return Response[city_schemas.CityDetailSchema](data=updated_city)


@router.delete(
    "/{city_id}",
    responses={
        **common_responses,
        **response_404,
    },
    description="by `HamzeZN`",
    status_code=204,
)
@return_on_failure
async def admin_delete_city(
    background_tasks: BackgroundTasks,
    city_id: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "delete"]),
):
    is_deleted = await city_controller.soft_delete_city(city_id=city_id)
    if is_deleted:
        background_tasks.add_task(
            func=log_controller.create_log,
            action=LogActionEnum.delete,
            action_by=current_user.id,
            entity=entity,
            entity_id=city_id,
        )
    return responses.Response(status_code=204)
