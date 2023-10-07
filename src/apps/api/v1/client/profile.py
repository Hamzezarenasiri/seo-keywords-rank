from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Security, status, Query
from starlette.responses import Response as StarletteResponse

from src.apps.auth.deps import get_current_customer
from src.apps.file.schema import FileOut
from src.apps.user import schema as user_schema
from src.apps.user.controller import profile_controller
from src.apps.user.enum import UserMessageEnum
from src.apps.user.models import UserDBReadModel
from src.core.base.schema import Response, PaginatedResponse
from src.core.mixins.fields import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses, response_413
from src.core.utils import return_on_failure
from src.core.validators import avatar_validation

profile_router = APIRouter()


@profile_router.get(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.ProfileGetMeOut],
)
@return_on_failure
async def my_profile(
    current_user: UserDBReadModel = Security(get_current_customer),
) -> Response[user_schema.ProfileGetMeOut]:
    result_data = await profile_controller.get_my_profile(current_user=current_user)
    return Response[user_schema.ProfileGetMeOut](data=result_data)


@profile_router.patch(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.ProfileUpdateMeOut],
)
@return_on_failure
async def update_profile(
    payload: user_schema.CustomerProfileUpdateMeIn,
    current_user: UserDBReadModel = Security(get_current_customer),
) -> Response[user_schema.ProfileUpdateMeOut]:
    result_data = await profile_controller.update_profile(
        current_user=current_user, payload=payload
    )
    return Response[user_schema.ProfileUpdateMeOut](data=result_data)


@profile_router.post(
    "/avatar",
    description="Upload user avatar",
    status_code=status.HTTP_200_OK,
    responses={
        **common_responses,
        **response_413,
    },
    response_model=Response[FileOut],
)
@return_on_failure
async def upload_avatar(
    avatar=Depends(avatar_validation),
    current_user: UserDBReadModel = Security(get_current_customer),
):
    result = await profile_controller.upload_avatar(
        avatar=avatar, current_user=current_user
    )
    return Response[FileOut](data=result)


@profile_router.delete(
    "/avatar",
    description="Remove user avatar",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **common_responses,
    },
)
@return_on_failure
async def delete_avatar(
    current_user: UserDBReadModel = Security(get_current_customer),
):
    await profile_controller.delete_avatar(current_user=current_user)
    return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)


@profile_router.get(
    "/addresses",
    status_code=status.HTTP_200_OK,
    responses={
        **common_responses,
    },
    response_model=Response[List[user_schema.AddressSchemaOut]],
)
@return_on_failure
async def get_all_addresses(
    current_user: UserDBReadModel = Security(get_current_customer),
) -> Response[user_schema.AddressSchemaOut]:
    result_data = await profile_controller.get_all_addresses(current_user=current_user)
    return Response[List[user_schema.AddressSchemaOut]](data=result_data)


@profile_router.post(
    "/addresses",
    status_code=status.HTTP_201_CREATED,
    responses={
        **common_responses,
    },
    response_model=Response[List[user_schema.AddressSchemaOut]],
    description="Add new address to client profile.",
)
@return_on_failure
async def create_new_address(
    payload: user_schema.AddressSchemaIn,
    current_user: UserDBReadModel = Security(get_current_customer),
) -> Response[List[user_schema.AddressSchemaOut]]:
    result_data = await profile_controller.create_new_address(
        payload=payload,
        current_user=current_user,
    )
    return Response[List[user_schema.AddressSchemaOut]](data=result_data)


@profile_router.get(
    "/addresses/{address_id}/",
    response_model=Response[user_schema.AddressSchemaOut],
    status_code=status.HTTP_200_OK,
    responses={
        **common_responses,
    },
)
@return_on_failure
async def get_single_address(
    address_id: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(get_current_customer),
) -> Response[user_schema.AddressSchemaOut]:
    result_data = await profile_controller.get_single_address(
        address_id=address_id,
        current_user=current_user,
    )
    return Response[user_schema.AddressSchemaOut](data=result_data)


@profile_router.delete(
    "/addresses/{address_id}/",
    responses={
        **common_responses,
    },
    description="Delete a particular address from client profile.",
    response_model=Response[List[user_schema.AddressSchemaOut]],
)
@return_on_failure
async def delete_single_address(
    address_id: SchemaID,
    current_user: UserDBReadModel = Security(
        get_current_customer,
    ),
):
    result_data = await profile_controller.delete_single_address(
        address_id=address_id,
        current_user=current_user,
    )
    return Response[List[user_schema.AddressSchemaOut]](data=result_data)


@profile_router.patch(
    "/addresses/{address_id}/",
    response_model=Response[user_schema.AddressSchemaOut],
    status_code=status.HTTP_200_OK,
    responses={
        **common_responses,
    },
    description="Update a particular address in client profile.",
)
@return_on_failure
async def update_single_address(
    payload: user_schema.AddressSchemaUpdateIn,
    address_id: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(
        get_current_customer,
    ),
) -> Response[user_schema.AddressSchemaOut]:
    result_data = await profile_controller.update_single_address(
        address_id=address_id,
        payload=payload,
        current_user=current_user,
    )
    return Response[user_schema.AddressSchemaOut](data=result_data)
