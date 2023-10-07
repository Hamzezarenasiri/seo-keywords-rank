import contextlib
from typing import Optional, Tuple

from fastapi import (
    Depends,
    HTTPException,
    Request,
    WebSocket,
    status,
    WebSocketException,
    Query,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from fastapi.security.utils import get_authorization_scheme_param

from src.apps.user import exception as user_exception
from src.apps.user.models import UserDBReadModel
from src.core.common.enums import RoleEnum
from src.core.token import token_helper
from . import exception
from .crud import permissions_crud
from .exception import UserForceLogin
from ..user.controller import user_controller


class JWTAuth(HTTPBearer):
    async def __call__(self, request: Request = None, websocket: WebSocket = None):
        request = request or websocket
        try:
            return await super().__call__(request)
        except HTTPException as exc:
            if websocket:
                raise WebSocketException(
                    code=status.WS_1008_POLICY_VIOLATION, reason=exc.detail
                ) from exc

            raise


jwt_authentication = JWTAuth()


async def get_user_obj(token):
    payload = await token_helper.verify_token(token.credentials)
    if payload.limited:
        raise exception.LimitedToken
    if not payload.user_id:
        raise exception.InvalidTokenProvided
    user_obj = await user_controller.find_by_user_id(user_id=payload.user_id)
    if not user_obj:
        raise user_exception.UserNotFound
    if user_obj.is_force_login:
        raise UserForceLogin
    if not user_obj.is_enable:
        raise user_exception.UserIsDisabled
    if user_obj.is_blocked:
        raise user_exception.UserIsBlocked
    if user_obj.email and not user_obj.email_verified:
        raise user_exception.UserEmailNotVerified(data=dict(username=user_obj.email))
    if user_obj.mobile_number and not user_obj.phone_verified:
        raise user_exception.UserPhoneNotVerified(
            data=dict(username=user_obj.mobile_number)
        )
    return user_obj


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(jwt_authentication),
    security_scopes: SecurityScopes = None,
) -> UserDBReadModel:
    user_obj = await get_user_obj(token)
    return await permissions_crud.check_permissions(security_scopes, user_obj)


async def get_admin_user(
    token: HTTPAuthorizationCredentials = Depends(jwt_authentication),
    security_scopes: SecurityScopes = None,
) -> UserDBReadModel:
    user_obj = await get_user_obj(token)
    if user_obj.role not in [RoleEnum.audit, RoleEnum.admin]:
        raise user_exception.AccessDenied
    return await permissions_crud.check_permissions(security_scopes, user_obj)


async def get_current_customer(
    token: HTTPAuthorizationCredentials = Depends(jwt_authentication),
) -> UserDBReadModel:
    return await get_user_obj(token)


optional_jwt_authentication = HTTPBearer(auto_error=False)


async def get_optional_current_user(
    token: Optional[HTTPAuthorizationCredentials] = Depends(
        optional_jwt_authentication
    ),
) -> Optional[UserDBReadModel]:
    if token:
        with contextlib.suppress(HTTPException):
            payload = await token_helper.verify_token(token.credentials)
            if not payload.limited and payload.user_id:
                user_obj = await user_controller.find_by_user_id(
                    user_id=payload.user_id
                )
                if user_obj:
                    return user_obj
    return None


async def get_user_limited_token(
    token: HTTPAuthorizationCredentials = Depends(jwt_authentication),
) -> Tuple[UserDBReadModel, bool]:
    payload = await token_helper.verify_token(token.credentials)
    user_obj = await user_controller.find_by_user_id(user_id=payload.user_id)
    if not user_obj:
        raise user_exception.UserNotFound
    if not user_obj.is_enable:
        raise user_exception.UserIsDisabled
    if user_obj.is_blocked:
        raise user_exception.UserIsBlocked
    return user_obj, payload.limited


async def get_audit_user(
    token: HTTPAuthorizationCredentials = Depends(jwt_authentication),
    security_scopes: SecurityScopes = None,
) -> UserDBReadModel:
    user_obj = await get_user_obj(token)
    if user_obj.role not in [RoleEnum.audit, RoleEnum.admin]:
        raise user_exception.AccessDenied
    return await permissions_crud.check_permissions(security_scopes, user_obj)


def ws_jwt_query_param(authorization: str = Query(...)):
    scheme, credentials = get_authorization_scheme_param(authorization)
    if scheme.lower() != "bearer":
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION,
            reason="Invalid authentication credentials",
        )
    return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


async def ws_get_current_customer(
    token: HTTPAuthorizationCredentials = Depends(ws_jwt_query_param),
) -> UserDBReadModel:
    try:
        return await get_user_obj(token)
    except HTTPException as exc:
        raise WebSocketException(
            code=status.WS_1008_POLICY_VIOLATION, reason=exc.detail
        ) from exc
