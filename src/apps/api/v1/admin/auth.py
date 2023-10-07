from fastapi import APIRouter, Query, Security

from src.apps.auth import schema as auth_schema
from src.apps.auth.controller import auth_controller
from src.apps.auth.deps import get_admin_user
from src.apps.auth.enum import AuthMessageEnum
from src.apps.user.models import UserDBReadModel
from src.core.base.schema import Response
from src.core.common.enums import RoleEnum
from src.core.common.models.token import RefreshRequest
from src.core.responses import (
    common_responses,
    response_404,
    response_500,
    response_401,
)
from src.core.utils import return_on_failure
from src.main.config import jwt_settings, facebook_settings

refresh_valid_seconds = jwt_settings.REFRESH_TOKEN_LIFETIME_SECONDS

admin_auth_router = APIRouter()


@admin_auth_router.post(
    "/login",
    responses={**response_404, **response_500},
    response_model=Response[auth_schema.AuthToken],
    description="By `Hamze.zn`",
)
@return_on_failure
async def login_username_password(
    user_pass: auth_schema.AuthUsernamePasswordIn,
):
    result_data = await auth_controller.login_username_password(
        user_pass=user_pass, roles=[RoleEnum.admin, RoleEnum.audit]
    )
    return Response[auth_schema.AuthToken](data=result_data)


@admin_auth_router.get(
    "/login/fb",
    responses={**response_404, **response_500},
    response_model=Response[auth_schema.AuthToken],
    description="By `Hamze.zn`",
)
@return_on_failure
async def facebook_login(
    code: str = Query(...),
):
    result_data = await auth_controller.fb_login(code=code)
    return Response[auth_schema.AuthToken](data=result_data)


@admin_auth_router.get(
    "/logout",
    responses={**common_responses},
    response_model=Response[auth_schema.UserGetLogoutOut],
)
@return_on_failure
async def logout_user(
    current_user: UserDBReadModel = Security(get_admin_user),
):
    result_data = await auth_controller.logout_user(current_user=current_user)
    return Response[auth_schema.UserGetLogoutOut](data=result_data)


@admin_auth_router.post(
    "/token/refresh",
    responses={
        **response_401,
        **response_500,
    },
    response_model=Response[auth_schema.AuthToken],
)
@return_on_failure
async def refresh_token(refresh_request: RefreshRequest):
    result_data = await auth_controller.refresh_token(refresh_request)
    return Response[auth_schema.AuthToken](
        data=result_data, message=AuthMessageEnum.refresh_token
    )


facebook_login_link = (
    f"https://www.facebook.com/v12.0/dialog/oauth?"
    f"client_id={facebook_settings.CLIENT_ID}"
    f"&redirect_uri={facebook_settings.REDIRECT_URI}"
)
