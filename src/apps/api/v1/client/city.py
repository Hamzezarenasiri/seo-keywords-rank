from typing import Optional, List
from fastapi import (
    APIRouter,
    Security,
    Depends,
    Query,
)
from src.core.mixins.fields import SchemaID
from src.main.config import collections_names
from src.core.utils import return_on_failure
from src.core.responses import common_responses
from src.core.base.schema import Response, PaginatedResponse
from src.core.pagination import Pagination
from src.core.ordering import Ordering
from src.apps.auth.deps import get_optional_current_user
from src.apps.user.models import UserDBReadModel
from src.apps.country.schema import CityListSchema
from src.apps.country.controller import city_controller

entity = collections_names.CITIES
router = APIRouter()


@router.get(
    "",
    responses={**common_responses},
    response_model=Response[PaginatedResponse[List[CityListSchema]]],
    description="by `HamzeZN`",
)
@return_on_failure
async def customer_get_cities(
    current_user: UserDBReadModel = Security(get_optional_current_user),
    state_id: Optional[SchemaID] = Query(None),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    criteria = {"is_enable": True}
    if state_id:
        criteria["state_id"] = state_id
    cities = await city_controller.get_list_objs(
        pagination=pagination,
        ordering=ordering,
        criteria=criteria,
        sub_list_schema=CityListSchema,
    )
    return Response[PaginatedResponse[List[CityListSchema]]](data=cities)
