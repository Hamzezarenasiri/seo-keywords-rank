from datetime import datetime, timezone
from pprint import pprint
from typing import Optional, List

import httpx
from fastapi import BackgroundTasks

from src.apps.user import exception as user_exceptions
from src.apps.user.controller import user_controller
from src.apps.user.crud import users_crud
from src.apps.user.models import UserDBReadModel
from src.apps.user.schema import CreateUserGroupEnum, UserSocialCreateSchema
from src.core import otp, token
from src.core.common import exceptions
from src.core.common.enums import RoleEnum
from src.core.common.models.security import UsernamePasswordSchema
from src.core.common.models.token import AuthToken, RefreshRequest
from src.core.mixins import Message, SchemaID
from src.core.mixins.models import USERNAME_IS_PHONE, USERNAME_IS_EMAIL
from src.core.otp import OtpExistsError, OtpRequestType
from src.core.password import generate_random_password
from src.main.config import facebook_settings, google_settings, app_settings
from src.services.db.mongodb import UpdateOperatorsEnum
from . import schema as auth_schema
from .crud import entities_crud, groups_crud
from .enum import AuthOTPTypeEnum
from .exception import (
    OTPExpiredOrInvalid,
    UserSocialLoginNotAcceptable,
    GroupsHaveUser,
    OtpExists,
)
from .models import GroupDBCreateModel, GroupDBReadModel
from ..user.enum import UserStatus, LoginType
from ..user.exception import (
    UserIsDisabled,
    UserIsBlocked,
    UserIsPending,
    UserIsRejected,
    GoogleCodeNotValid,
    UserEmailNotVerified,
    UserPhoneNotVerified,
)
from ...core.base.controller import BaseController
from ...core.base.schema import PaginatedResponse
from ...core.ordering import Ordering
from ...core.pagination import Pagination


class AuthController(object):
    @staticmethod
    async def login_username_password(user_pass, roles=None):
        if roles is None:
            roles = [RoleEnum.customer, RoleEnum.admin]
        user = await user_controller.authenticate_by_username_pass(
            username=user_pass.username,
            password=user_pass.password,
            and_conditions={"role": {"$in": roles}},
        )
        if not user:
            raise user_exceptions.UserNotFound
        if not user.is_enable:
            raise user_exceptions.UserIsDisabled
        if (
            user.email
            and not user.email_verified
            and user_pass.username["value_type"] == USERNAME_IS_EMAIL
        ):
            raise UserEmailNotVerified(data=dict(username=user.email))
        elif (
            user.mobile_number
            and not user.phone_verified
            and user_pass.username["value_type"] == USERNAME_IS_PHONE
        ):
            raise UserPhoneNotVerified(data=dict(username=user.mobile_number))
        await users_crud.update(
            criteria={"id": user.id},
            new_doc={
                "login_datetime": datetime.now(timezone.utc),
                "last_login_datetime": user.login_datetime,
                "is_force_login": False,
            },
            operator=UpdateOperatorsEnum.set_,
        )
        return await token.generate_token(user.id, user.role)

    @staticmethod
    async def access_token(
        user_pass: UsernamePasswordSchema,
    ):
        if user_pass.password:
            user = await user_controller.authenticate_by_username_pass(
                username=user_pass.username,
                password=user_pass.password,
            )
        else:
            user = await user_controller.find_by_username(
                username=user_pass.username,
            )
        if not user:
            raise user_exceptions.UserNotFound

        if not user.is_enable:
            raise user_exceptions.UserIsDisabled
        if user.is_blocked:
            raise user_exceptions.UserIsBlocked
        if user.email and not user.email_verified:
            raise UserEmailNotVerified(data=dict(username=user.email))
        if user.mobile_number and not user.phone_verified:
            raise UserPhoneNotVerified(data=dict(username=user.mobile_number))
        await users_crud.update(
            criteria={"id": user.id},
            new_doc={
                "login_datetime": datetime.now(timezone.utc),
                "last_login_datetime": user.login_datetime,
                "is_force_login": False,
            },
            operator=UpdateOperatorsEnum.set_,
        )
        return await token.generate_token(user.id, user.role)

    async def otp_request(
        self,
        request_payload: auth_schema.AuthUserForgetOtpReqIn,
        background_tasks: BackgroundTasks,
        request_type: Optional[OtpRequestType] = OtpRequestType.reset_pass,
    ) -> Message:
        username = request_payload.username
        otp_type = {
            USERNAME_IS_PHONE: AuthOTPTypeEnum.sms,
            USERNAME_IS_EMAIL: AuthOTPTypeEnum.email,
        }[username["value_type"]]
        user_obj = await user_controller.find_by_username(username)
        if user_obj:
            background_tasks.add_task(
                func=otp.set_otp_and_send_message,
                user=user_obj,
                otp_type=otp_type,
                cache_key=username["value"],
                request_type=request_type,
            )
            return Message()

            # await otp.set_otp_and_send_message(
            #     user=user_obj,
            #     otp_type=otp_type,
            #     cache_key=username["value"],
            #     request_type=request_type,
            # )
            # return Message()
        else:
            raise user_exceptions.UserNotFound

    @staticmethod
    async def verify_otp(
        verification: auth_schema.AuthOTPVerifyIn,
    ) -> auth_schema.AuthToken:
        user = await user_controller.find_by_username(username=verification.username)
        if not user:
            raise user_exceptions.UserNotFound
        if (
            await otp.get_otp(key=verification.username.value)
            != verification.verification_code
        ):
            raise OTPExpiredOrInvalid
        new_doc = {
            "login_datetime": datetime.now(timezone.utc),
            "last_login_datetime": user.login_datetime,
        }
        if verification.username.value_type == USERNAME_IS_EMAIL:
            new_doc["email_verified"] = True
        elif verification.username.value_type == USERNAME_IS_PHONE:
            new_doc["phone_verified"] = True
        await users_crud.update(
            criteria={"id": user.id},
            new_doc=new_doc,
            operator=UpdateOperatorsEnum.set_,
        )
        return await token.generate_token(user.id, user.role)

    @staticmethod
    async def limited_verify_otp(
        verification: auth_schema.AuthOTPVerifyIn,
    ) -> auth_schema.AuthForgetVerifyOut:
        user = await user_controller.find_by_username(username=verification.username)
        if not user:
            raise user_exceptions.UserNotFound
        if (
            await otp.get_otp(key=verification.username.value)
            != verification.verification_code
        ):
            raise OTPExpiredOrInvalid
        generated_tokens = await token.generate_token(
            user_id=str(user.id),
            role=user.role,
            limited=True,
        )
        return auth_schema.AuthForgetVerifyOut(
            access_token=generated_tokens.access_token,
            limited=True,
        )

    @staticmethod
    async def refresh_token(
        refresh_request: RefreshRequest,
    ) -> AuthToken:
        return await token.generate_refresh_token(refresh_request.refresh_token)

    async def fb_login(self, code: str) -> auth_schema.AuthToken:
        a_url = (
            f"https://graph.facebook.com/v11.0/oauth/access_token?"
            f"client_id={facebook_settings.CLIENT_ID}"
            f"&redirect_uri={facebook_settings.REDIRECT_URI}"
            f"&client_secret={facebook_settings.CLIENT_SECRET}"
            f"&code={code}"
        )
        async with httpx.AsyncClient() as client:
            a_res = await client.get(a_url)
            access_token = a_res.json().get("access_token")
            client.headers.update({"Authorization": f"Bearer {access_token}"})
            b_res = await client.get(
                "https://graph.facebook.com/me?"
                "fields=id,name,email,first_name,last_name,picture,gender"
            )
        res_json = b_res.json()
        if b_res.status_code != 200:
            raise UserSocialLoginNotAcceptable
        return await self.social_register_and_login(
            user_email=res_json.get("email"),
            first_name=res_json.get("first_name"),
            last_name=res_json.get("last_name"),
            password=generate_random_password(),
            avatar_url=res_json.get("picture", {}).get("date", {}).get("url"),
            email_verified=bool(res_json.get("email")),
            gender=res_json.get("gender"),
        )

    async def fb_login_access_token(self, access_token: str) -> auth_schema.AuthToken:
        async with httpx.AsyncClient() as client:
            client.headers.update({"Authorization": f"Bearer {access_token}"})
            b_res = await client.get(
                "https://graph.facebook.com/me?"
                "fields=id,name,email,first_name,last_name,picture,gender"
            )
        res_json = b_res.json()
        if b_res.status_code != 200:
            raise UserSocialLoginNotAcceptable
        return await self.social_register_and_login(
            user_email=res_json.get("email"),
            first_name=res_json.get("first_name"),
            last_name=res_json.get("last_name"),
            password=generate_random_password(),
            avatar_url=res_json.get("picture", {}).get("date", {}).get("url"),
            email_verified=bool(res_json.get("email")),
            gender=res_json.get("gender"),
        )

    async def google_login(self, code: str) -> auth_schema.AuthToken:
        a_url = "https://oauth2.googleapis.com/token"
        a_payload_body = {
            "code": code,
            "client_id": google_settings.CLIENT_ID,
            "redirect_uri": google_settings.LOGIN_REDIRECT_URI,
            "client_secret": google_settings.CLIENT_SECRET,
            "grant_type": "authorization_code",
        }
        b_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        async with httpx.AsyncClient() as client:
            a_res = await client.post(a_url, json=a_payload_body)
            access_token = a_res.json().get("access_token")
            client.headers.update({"Authorization": f"Bearer {access_token}"})
            b_res = await client.get(b_url)
        if b_res.status_code != 200:
            pprint(b_res.json())
            raise GoogleCodeNotValid(detail=[{"response": b_res.json()}])
        res_json = b_res.json()
        return await self.social_register_and_login(
            user_email=res_json["email"],
            first_name=res_json.get("given_name"),
            last_name=res_json.get("family_name"),
            password=generate_random_password(),
            avatar_url=res_json.get("picture"),
            email_verified=bool(res_json.get("email")),
        )

    async def google_login_id_token(self, id_token: str) -> auth_schema.AuthToken:
        b_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        async with httpx.AsyncClient() as client:
            b_res = await client.get(b_url)
        if b_res.status_code != 200:
            pprint(b_res.json())
            raise GoogleCodeNotValid(detail=[{"response": b_res.json()}])
        res_json = b_res.json()
        return await self.social_register_and_login(
            user_email=res_json.get("email"),
            first_name=res_json.get("given_name"),
            last_name=res_json.get("family_name"),
            password=generate_random_password(),
            avatar_url=res_json.get("picture"),
            email_verified=bool(res_json.get("email")),
        )

    async def social_register_and_login(
        self,
        user_email: str,
        first_name: str,
        last_name: str,
        password: str,
        avatar_url: Optional[str] = None,
        email_verified: Optional[bool] = False,
        **kwargs,
    ) -> auth_schema.AuthToken:
        if not user_email:
            raise UserSocialLoginNotAcceptable
        user = await users_crud.get_object(
            dict(email=user_email), raise_exception=False
        ) or await user_controller.create_new_user(
            UserSocialCreateSchema(
                email=user_email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role=RoleEnum.customer.value,
                groups=[CreateUserGroupEnum.customer.value],
                avatar=avatar_url,
                user_status=UserStatus.just_joined,
                addresses=[],
                permissions=[],
            ),
            login_type=LoginType.social,
            email_verified=email_verified,
            **kwargs,
        )
        if not user.is_enable:
            raise UserIsDisabled
        if user.is_blocked:
            raise UserIsBlocked
        if user.user_status == UserStatus.pending:
            raise UserIsPending
        if user.user_status == UserStatus.rejected:
            raise UserIsRejected
        new_doc = {
            "login_datetime": datetime.now(timezone.utc),
            "last_login_datetime": user.login_datetime,
            "email_verified": email_verified,
        }
        await users_crud.update(
            criteria={"id": user.id},
            new_doc=new_doc,
            operator=UpdateOperatorsEnum.set_,
        )
        return await token.generate_token(user.id, user.role)

    async def logout_user(
        self,
        current_user: UserDBReadModel,
        user_id: SchemaID = None,
    ) -> auth_schema.UserGetLogoutOut:
        if user_id:
            user = await users_crud.get_object(criteria={"id": user_id})
        else:
            user = current_user
        updated_target_user, is_updated = await users_crud.update_and_get(
            criteria={"id": user.id}, new_doc={"is_force_login": True}
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return auth_schema.UserGetLogoutOut(
            force_login=updated_target_user.is_force_login
        )

    @staticmethod
    async def customer_request_login_otp(
        background_tasks: BackgroundTasks,
        payload: auth_schema.CustomerRequestLoginOTPIn,
    ):
        try:
            token = await otp.cache_otp_verification(key=payload.username["value"])
        except OtpExistsError as e:
            raise OtpExists from e
        if not app_settings.TEST_MODE:
            otp_type = {
                USERNAME_IS_EMAIL: AuthOTPTypeEnum.email.value,
                USERNAME_IS_PHONE: AuthOTPTypeEnum.sms.value,
            }
            background_tasks.add_task(
                func=otp.send_otp_verification,
                reciever=payload.username["value"],
                otp_code=token,
                otp_type=otp_type[payload.username["value_type"]],
            )

    @staticmethod
    async def login_or_register(
        payload: auth_schema.CustomerVerifyLoginOTPIn,
    ) -> auth_schema.AuthToken:
        await otp.verify_otp(
            key=payload.username["value"], code=payload.verification_code
        )
        user = await user_controller.find_by_username(
            username=payload.username, raise_exception=False
        ) or await user_controller.customer_register(payload=payload)
        await users_crud.update(
            criteria={"id": user.id},
            new_doc={
                "login_datetime": datetime.now(timezone.utc),
                "last_login_datetime": user.login_datetime,
                "is_force_login": False,
            },
            operator=UpdateOperatorsEnum.set_,
        )
        return await token.generate_token(user.id, user.role)


auth_controller = AuthController()


class GroupController(BaseController):
    async def create_new_group(
        self,
        new_group_data: auth_schema.GroupCreateIn,
    ) -> auth_schema.GroupCreateOut:
        for permission in new_group_data.permissions:
            diff = set(permission.rules).difference(
                set(await entities_crud.get_entity_rules(permission.entity))
            )
            if diff:
                raise exceptions.CustomHTTPException(
                    status_code=422,
                    detail=[f"{diff} rules not found"],
                    message=f"{diff} rules not found",
                )

        created = await self.crud.create(
            GroupDBCreateModel(**new_group_data.dict(exclude_none=True))
        )
        return auth_schema.GroupCreateOut(**created.dict())

    async def get_all_group(
        self,
        pagination: Pagination,
        ordering: Ordering,
        criteria: dict = None,
    ) -> PaginatedResponse[List[auth_schema.GroupGetListOut]]:
        query = {}
        if criteria:
            query |= criteria
        return await pagination.paginate(
            crud=self.crud,
            list_item_model=auth_schema.GroupGetListOut,
            criteria=query,
            _sort=await ordering.get_ordering_criteria(),
        )

    async def get_single_group(self, target_group_name: str) -> auth_schema.GroupGetOut:
        target_group = await self.crud.get_object(criteria=dict(name=target_group_name))
        return auth_schema.GroupGetOut(**target_group.dict())

    async def update_single_group(
        self,
        target_group_name: str,
        new_group_data: auth_schema.GroupUpdateIn,
    ) -> auth_schema.GroupUpdateOut:
        await groups_crud.get_by_id(
            _id=target_group_name,
        )
        if new_group_data.permissions:
            for permission in new_group_data.permissions:
                diff = set(permission.rules).difference(
                    set(await entities_crud.get_entity_rules(permission.entity))
                )
                if diff:
                    raise exceptions.CustomHTTPException(
                        status_code=422,
                        detail=[f"{diff} rules not found"],
                        message=f"{diff} rules not found",
                    )
        (updated_group, is_updated) = await self.crud.default_update_and_get(
            criteria=dict(name=target_group_name),
            new_doc=new_group_data.dict(exclude_none=True),
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return auth_schema.GroupUpdateOut(**updated_group.dict())

    async def soft_delete_single_group(self, name: str) -> bool:
        target_group = await self.crud.get_object(criteria=dict(name=name))
        is_deleted = await self.crud.soft_delete(criteria=dict(name=name))
        if target_group and is_deleted:
            return is_deleted
        else:
            raise exceptions.DeleteFailed

    async def bulk_delete_groups(
        self,
        obj_ids: List[SchemaID],
    ) -> List[GroupDBReadModel]:
        groups_have_user_ids_ = await users_crud.get_list_of_a_field_values(
            target_field="groups",
            criteria={"groups": {"$in": obj_ids}},
        )
        if groups_have_user_ids_:
            groups_have_user_ids = {
                val for sublist in groups_have_user_ids_ for val in sublist
            }
        else:
            groups_have_user_ids = []
        updated_users = await self.crud.bulk_soft_delete(
            obj_ids=list(set(obj_ids).difference(groups_have_user_ids))
        )
        if groups_have_user_ids:
            raise GroupsHaveUser(data={"groups_have_user": groups_have_user_ids})

        return updated_users


group_controller = GroupController(crud=groups_crud)
