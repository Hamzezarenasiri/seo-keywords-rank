from typing import List
from fastapi import (
    APIRouter,
    Security,
    Depends,
)
from src.main.config import collections_names
from src.core.utils import return_on_failure
from src.core.responses import common_responses
from src.core.base.schema import Response, PaginatedResponse
from src.core.pagination import Pagination
from src.core.ordering import Ordering
from src.apps.auth.deps import get_optional_current_user
from src.apps.user.models import UserDBReadModel
from src.apps.country.schema import StateListSchema
from src.apps.country.controller import state_controller

entity = collections_names.STATES
router = APIRouter()


@router.get(
    "",
    responses={**common_responses},
    response_model=Response[PaginatedResponse[List[StateListSchema]]],
    description="by `HamzeZN`",
)
@return_on_failure
async def customer_get_states(
    current_user: UserDBReadModel = Security(get_optional_current_user),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    criteria = {"is_enable": True}
    states = await state_controller.get_list_objs(
        pagination=pagination,
        ordering=ordering,
        criteria=criteria,
        sub_list_schema=StateListSchema,
    )
    return Response[PaginatedResponse[List[StateListSchema]]](data=states)
