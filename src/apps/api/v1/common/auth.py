from typing import Tuple, Union

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Security

from src.apps.auth import schema as auth_schema
from src.apps.auth.controller import auth_controller
from src.apps.auth.deps import get_current_user, get_user_limited_token
from src.apps.auth.enum import (
    AuthConflict409MessageEnum,
    AuthMessageEnum,
)
from src.apps.user.controller import user_controller
from src.apps.user.models import UserDBReadModel
from src.core.base.schema import ErrorResponse, Response
from src.core.common.models.token import RefreshRequest
from src.core.otp import OtpRequestType
from src.core.responses import (
    common_responses,
    response_401,
    response_404,
    response_500,
)
from src.core.utils import return_on_failure
from src.main.config import (
    facebook_settings,
    google_settings,
    jwt_settings,
)

refresh_valid_seconds = jwt_settings.REFRESH_TOKEN_LIFETIME_SECONDS

auth_router = APIRouter()


@auth_router.post(
    "/otp/send",
    description="username( `email` or `mobile_number`)\n\n"
    "if entered username is `email` >> `mail` otp to entered email\n\n"
    # "if entered username is `phone` >> `sms` otp to entered phone\n\n"
    "By `Hamze.zn`",
    responses={
        **response_404,
        **response_500,
    },
    response_model=Response,
)
@return_on_failure
async def otp_reset_pass_request(
    background_tasks: BackgroundTasks,
    payload: auth_schema.AuthUserForgetOtpReqIn,
):
    result_detail = await auth_controller.otp_request(
        request_payload=payload,
        background_tasks=background_tasks,
        request_type=OtpRequestType.reset_pass,
    )

    return Response(detail=result_detail.detail, message=AuthMessageEnum.otp_request)


@auth_router.post(
    "/otp/send-verification-request",
    description="username( `email` or `mobile_number`)\n\n"
    "if entered username is `email` >> `mail` otp to entered email\n\n"
    # "if entered username is `phone` >> `sms` otp to entered phone\n\n"
    "By `Hamze.zn`",
    responses={
        **response_404,
        **response_500,
    },
    response_model=Response,
)
@return_on_failure
async def otp_verification_request(
    background_tasks: BackgroundTasks,
    payload: auth_schema.AuthUserForgetOtpReqIn,
):
    result_detail = await auth_controller.otp_request(
        request_payload=payload,
        background_tasks=background_tasks,
        request_type=OtpRequestType.verification,
    )

    return Response(detail=result_detail.detail, message=AuthMessageEnum.otp_request)


@auth_router.post(
    "/otp/verify",
    responses={
        **response_404,
        **response_500,
    },
    response_model=Response[auth_schema.AuthToken],
)
@return_on_failure
async def otp_verify(verification: auth_schema.AuthOTPVerifyIn):
    result_data = await auth_controller.verify_otp(verification=verification)
    return Response[auth_schema.AuthToken](data=result_data)


@auth_router.post(
    "/password/forgot/verify",
    responses={
        **response_404,
        **response_500,
    },
    response_model=Response[auth_schema.AuthForgetVerifyOut],
)
@return_on_failure
async def otp_verify_limited(
    verification: auth_schema.AuthOTPVerifyIn,
):
    result_data = await auth_controller.limited_verify_otp(verification=verification)
    return Response[auth_schema.AuthForgetVerifyOut](
        data=result_data, message=AuthMessageEnum.otp_verify_limited
    )


@auth_router.post(
    "/password/change",
    responses={
        409: {"model": ErrorResponse[AuthConflict409MessageEnum]},
        **response_500,
    },
    response_model=Response[
        Union[
            auth_schema.AuthUserResetPasswordOut,
            auth_schema.AuthChangedPasswordMessageOut,
        ]
    ],
    description="`old_password` is `optional`:"
    "\n\nif token `limited` is `true`:`old_password` not `required` "
    "\n\n else: `old_password` is `required`\n\nBy `Hamze.zn`",
)
@return_on_failure
async def change_password(
    payload: auth_schema.AuthUserChangePasswordIn,
    current_user_limited: Tuple[UserDBReadModel, bool] = Depends(
        get_user_limited_token
    ),
):
    current_user, is_limited = current_user_limited
    result_data, is_changed = await user_controller.change_password(
        verification=payload, current_user=current_user, is_limited=is_limited
    )
    if is_changed:
        message = AuthMessageEnum.changed_password
        success = True
    else:
        message = AuthMessageEnum.changed_password_failed
        success = False
    return Response[
        Union[
            auth_schema.AuthUserResetPasswordOut,
            auth_schema.AuthChangedPasswordMessageOut,
            auth_schema.AuthChangedPasswordErrorMessageOut,
        ]
    ](
        data=result_data,
        success=success,
        message=message,
        detail=[message],
    )


@auth_router.post(
    "/token/refresh",
    responses={
        **response_401,
        **response_500,
    },
    response_model=Response[auth_schema.AuthToken],
)
@return_on_failure
async def refresh_token(
    refresh_request: RefreshRequest,
):
    result_data = await auth_controller.refresh_token(refresh_request)
    return Response[auth_schema.AuthToken](
        data=result_data, message=AuthMessageEnum.refresh_token
    )


facebook_login_link = (
    f"https://www.facebook.com/v12.0/dialog/oauth?"
    f"client_id={facebook_settings.CLIENT_ID}"
    f"&redirect_uri={facebook_settings.REDIRECT_URI}"
)


@auth_router.get(
    "/login/fb",
    responses={
        **response_404,
        **response_500,
    },
    response_model=Response[auth_schema.AuthToken],
    description=f"By `Hamze.zn`\n\n Open this link in your browser:\n\n"
    f"`{facebook_login_link}`\n\nOR\n\n click on the following link:\n\n"
    f'<a href="{facebook_login_link}" target="_blank">FB Login :)</a>',
)
@return_on_failure
async def facebook_login(
    code: str = Query(...),
):
    result_data = await auth_controller.fb_login(code=code)
    return Response[auth_schema.AuthToken](
        data=result_data, message=AuthMessageEnum.facebook_login
    )


@auth_router.get(
    "/login/fb_token",
    responses={
        **response_404,
        **response_500,
    },
    response_model=Response[auth_schema.AuthToken],
)
@return_on_failure
async def facebook_login_access_token(
    access_token: str = Query(...),
):
    result_data = await auth_controller.fb_login_access_token(access_token=access_token)
    return Response[auth_schema.AuthToken](
        data=result_data, message=AuthMessageEnum.facebook_login
    )


google_login_link = (
    f"https://accounts.google.com/o/oauth2/v2/auth?"
    f"client_id={google_settings.CLIENT_ID}"
    f"&redirect_uri={google_settings.LOGIN_REDIRECT_URI}"
    f"&response_type=code&scope=profile email"
    f"&include_granted_scopes=true&access_type=offline"
)


@auth_router.get(
    "/login/google",
    responses={
        **response_404,
        **response_500,
    },
    response_model=Response[auth_schema.AuthToken],
    description=f"By `Hamze.zn`\n\n Open this link in your browser:\n\n"
    f"`{google_login_link}`\n\nOR\n\n click on the following link:\n\n"
    f'<a href="{google_login_link}" target="_blank">Google Login :)</a>',
)
@return_on_failure
async def google_login(code: str = Query(...)):
    result_data = await auth_controller.google_login(code=code)
    return Response[auth_schema.AuthToken](
        data=result_data, message=AuthMessageEnum.google_login
    )


@auth_router.get(
    "/login/google_token",
    responses={
        **response_404,
        **response_500,
    },
    response_model=Response[auth_schema.AuthToken],
)
@return_on_failure
async def google_login_id_token(id_token: str = Query(...)):
    result_data = await auth_controller.google_login_id_token(id_token=id_token)
    return Response[auth_schema.AuthToken](
        data=result_data, message=AuthMessageEnum.google_login
    )


@auth_router.get(
    "/logout",
    responses={
        **common_responses,
    },
    response_model=Response[auth_schema.UserGetLogoutOut],
)
@return_on_failure
async def logout_user(
    current_user: UserDBReadModel = Security(get_current_user),
):
    result_data = await auth_controller.logout_user(current_user=current_user)
    return Response[auth_schema.UserGetLogoutOut](
        data=result_data, message=AuthMessageEnum.logout_user
    )
