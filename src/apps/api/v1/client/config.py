from fastapi import APIRouter
from starlette import status

from src.apps.config import schema as config_schema
from src.apps.config.controller import config_controller
from src.core.base.schema import Response
from src.core.responses import common_responses
from src.core.utils import return_on_failure

config_router = APIRouter()


@config_router.get(
    "",
    status_code=status.HTTP_200_OK,
    responses={
        **common_responses,
    },
    response_model=Response[config_schema.ConfigGetOut],
    response_model_exclude_none=True,
    description="Get configurations",
)
@return_on_failure
async def get_configs():
    result_data = await config_controller.get_configs()
    return Response[config_schema.ConfigGetOut](data=result_data)
