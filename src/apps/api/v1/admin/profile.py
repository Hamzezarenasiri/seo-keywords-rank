from fastapi import APIRouter, Security, Depends
from starlette import status
from starlette.responses import Response as StarletteResponse

from src.apps.auth.deps import get_audit_user
from src.apps.file.schema import FileOut
from src.apps.user import schema as user_schema
from src.apps.user.controller import profile_controller
from src.apps.user.models import UserDBReadModel
from src.core.base.schema import Response
from src.core.responses import common_responses, response_413
from src.core.utils import return_on_failure
from src.core.validators import avatar_validation
from src.main.config import collections_names, app_settings

profile_router = APIRouter()
entity = collections_names.USERS


# @profile_router.get(
#     "",
#     responses={
#         **common_responses,
#     },
#     response_model=Response[user_schema.ProfileGetMeOut],
#     description="Get admin profile data",
# )
# @return_on_failure
# async def my_profile(
#     current_user: UserDBReadModel = Security(get_admin_user),
# ) -> Response[user_schema.ProfileGetMeOut]:
#     result_data = await profile_controller.get_my_profile(current_user=current_user)
#     return Response[user_schema.ProfileGetMeOut](data=result_data)
#
#
# @profile_router.get(
#     "/permissions",
#     responses={
#         **common_responses,
#     },
#     response_model=Response[user_schema.ProfileGetPermssions],
#     description="Get User Permissions",
# )
# @return_on_failure
# async def my_permissions(
#     current_user: UserDBReadModel = Security(get_admin_user),
# ) -> Response[user_schema.ProfileGetPermssions]:
#     result_data = await profile_controller.get_my_permissions(current_user=current_user)
#     return Response[user_schema.ProfileGetPermssions](data=result_data)
#
#
# @profile_router.get(
#     "/permissions_dict",
#     responses={
#         **common_responses,
#     },
#     response_model=Response[user_schema.ProfileGetPermssionsDict],
#     description="Get User Permissions",
# )
# @return_on_failure
# async def get_my_permissions_dict(
#     current_user: UserDBReadModel = Security(get_admin_user),
# ) -> Response[user_schema.ProfileGetPermssionsDict]:
#     result_data = await profile_controller.get_my_permissions_dict(
#         current_user=current_user
#     )
#     return Response[user_schema.ProfileGetPermssionsDict](data=result_data)
#
#
# @profile_router.patch(
#     "",
#     responses={
#         **common_responses,
#     },
#     response_model=Response[user_schema.ProfileGetMeOut],
#     description="Update admin profile record",
# )
# @return_on_failure
# async def update_my_profile(
#     payload: user_schema.ProfileUpdateMeIn,
#     current_user: UserDBReadModel = Security(
#         get_admin_user,
#         scopes=[entity, "update"],
#     ),
# ) -> Response[user_schema.ProfileGetMeOut]:
#     if current_user.role != RoleEnum.admin:
#         raise user_exception.AccessDenied
#     result_data = await profile_controller.update_profile(
#         current_user=current_user,
#         payload=payload,
#     )
#     return Response[user_schema.ProfileGetMeOut](data=result_data)
@profile_router.get(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.ProfileGetMeOut],
)
@return_on_failure
async def my_profile(
    current_user: UserDBReadModel = Security(get_audit_user),
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
    payload: user_schema.AuditProfileUpdateMeIn,
    current_user: UserDBReadModel = Security(get_audit_user),
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
    current_user: UserDBReadModel = Security(get_audit_user),
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
    current_user: UserDBReadModel = Security(get_audit_user),
):
    await profile_controller.delete_avatar(current_user=current_user)
    return StarletteResponse(status_code=status.HTTP_204_NO_CONTENT)
