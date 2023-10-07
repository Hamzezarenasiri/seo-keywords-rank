from fastapi import (
    APIRouter,
    BackgroundTasks,
)
from src.main.config import collections_names
from src.core.base.schema import ErrorResponse, Response
from src.core.responses import response_500
from src.core.utils import return_on_failure
from src.apps.auth import schema as auth_schema
from src.apps.auth.controller import auth_controller
from src.apps.auth import enum as auth_enum

entity = collections_names.USERS
router = APIRouter()


@router.post(
    "/login/otp",
    responses={
        **response_500,
        406: {"model": ErrorResponse[auth_enum.OTPExistsErrorMessageEnum]},
    },
    response_model=Response,
    description="send verfication code for login\n\n by `HamzeZN`",
)
@return_on_failure
async def login_request_verification_otp(
    background_tasks: BackgroundTasks,
    payload: auth_schema.CustomerRequestLoginOTPIn,
):
    await auth_controller.customer_request_login_otp(
        background_tasks=background_tasks,
        payload=payload,
    )
    return Response(message="verification code has been sent to you")


@router.post(
    "/login/verify",
    responses={
        **response_500,
        404: {"model": ErrorResponse[auth_enum.OTPExpiredErrorMessageEnum]},
    },
    response_model=Response[auth_schema.AuthToken],
    description="login or register and login by verification code that has been sent to you\n\n"
    "by `HamzeZN`",
)
@return_on_failure
async def login_verify(
    payload: auth_schema.CustomerVerifyLoginOTPIn,
):
    result = await auth_controller.login_or_register(
        payload=payload,
    )
    return Response[auth_schema.AuthToken](data=result)
