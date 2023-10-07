import asyncio
import os
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Union
from uuid import uuid4

import user_agents
from fastapi import HTTPException, BackgroundTasks
from pymongo.errors import DuplicateKeyError
from starlette import status

from src.apps.auth.exception import (
    OldPasswordNotMatch,
    UserRegisterEmailExists,
    UserRegisterPhoneExists,
)
from src.apps.auth.schema import (
    AuthChangedPasswordErrorMessageOut,
    AuthChangedPasswordMessageOut,
    AuthUserChangePasswordIn,
    AuthUserResetPasswordOut,
    AuthToken,
    AuthRegisterIn,
    CustomerVerifyLoginOTPIn,
)
from src.apps.file.crud import files_crud
from src.apps.file.schema import FileOut, ValidatedFile
from src.apps.user.crud import users_crud
from src.apps.user.enum import (
    BusinessTypeEnum,
    UserStatus,
    UserMessageEnum,
    DefaultGroupNameEnum,
)
from src.apps.user.models import (
    UserDBCreateModel,
    UserDBUpdateModel,
    DeviceDetail,
    UserDevicesModel,
    BlockInfoModel,
)
from src.apps.user.schema import (
    UserCreateSchema,
    UsersActivationUserPatchOut,
    UsersBlockingUserPatchOut,
    UsersGetCustomerSubListOut,
    UsersGetUserOut,
    UsersGetUserSubListOut,
    UsersUpdateUserIn,
    AddNewDeviceIn,
    UserCreateSchemaOut,
    AuditUpdateUserIn,
)
from src.core import token, otp
from src.core.base.controller import BaseController
from src.core.base.schema import PaginatedResponse, Response
from src.core.common import exceptions
from src.core.common.enums.auth import RoleEnum
from src.core.common.exceptions import DeleteFailed, UpdateFailed
from src.core.firebase import subscribe_to_topic
from src.core.mixins.fields import SchemaID
from src.core.mixins.models import USERNAME_IS_EMAIL, USERNAME_IS_PHONE
from src.core.ordering import Ordering
from src.core.otp import OtpRequestType
from src.core.pagination import Pagination
from src.core.security import user_password
from src.services import global_services
from src.services.db.mongodb import UpdateOperatorsEnum
from . import schema as user_schema
from .exception import UserIsDisabled, UserIsBlocked, UserIsPending, UserIsRejected
from .models import UserDBReadModel
from ..auth.crud import permissions_crud
from ..auth.enum import AuthOTPTypeEnum
from ..auth.models import PermissionModel


class UserController(BaseController):
    @staticmethod
    async def find_by_user_id(
        user_id: SchemaID,
    ) -> Optional[UserDBReadModel]:
        user = await users_crud.get_object({"id": user_id})
        return user or None

    @staticmethod
    async def find_by_username(
        username: dict,
        and_conditions: Optional[dict] = None,
        raise_exception: bool = True,
    ) -> Optional[UserDBReadModel]:
        if and_conditions is None:
            and_conditions = {}
        query_options = {
            USERNAME_IS_EMAIL: {USERNAME_IS_EMAIL: username["value"]},
            USERNAME_IS_PHONE: {USERNAME_IS_PHONE: username["value"]},
        }
        query: dict = query_options[username["value_type"]]
        query |= and_conditions
        user_obj = await users_crud.get_object(query, raise_exception=raise_exception)
        return user_obj or None

    async def authenticate_by_username_pass(
        self,
        username: dict,
        password: str,
        and_conditions: Optional[dict] = None,
    ) -> Optional[UserDBReadModel]:
        user_obj = await self.find_by_username(
            username=username, and_conditions=and_conditions
        )
        if user_obj and user_password.verify_password(
            password, user_obj.hashed_password
        ):
            return user_obj
        return None

    async def change_password(
        self,
        verification: AuthUserChangePasswordIn,
        current_user: UserDBReadModel,
        is_limited: bool,
    ) -> Tuple[
        Union[
            AuthUserResetPasswordOut,
            AuthChangedPasswordMessageOut,
            AuthChangedPasswordErrorMessageOut,
        ],
        bool,
    ]:
        if not is_limited:
            if not verification.old_password:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=[
                        {
                            "loc": ["body", "old_password"],
                            "msg": "Enter old_password",
                        }
                    ],
                )
            if not user_password.verify_password(
                verification.old_password, current_user.hashed_password
            ):
                raise OldPasswordNotMatch
        if await self.set_password(
            user_id=current_user.id,
            new_password=verification.new_password,
        ):
            if is_limited:
                await users_crud.update(
                    criteria={"id": current_user.id},
                    new_doc={
                        "login_datetime": datetime.now(timezone.utc),
                        "last_login_datetime": current_user.login_datetime,
                    },
                    operator=UpdateOperatorsEnum.set_,
                )
                tokens = await token.generate_token(current_user.id, current_user.role)
                return (
                    AuthUserResetPasswordOut(
                        access_token=tokens.access_token,
                        refresh_token=tokens.refresh_token,
                    ),
                    True,
                )
            else:
                return AuthChangedPasswordMessageOut(), True
        else:
            return AuthChangedPasswordErrorMessageOut(), False

    @staticmethod
    async def set_password(
        user_id: SchemaID,
        new_password: str,
        force_change_password: bool = False,
        force_login: bool = False,
    ) -> bool:
        _, is_updated = await users_crud.update_and_get(
            criteria={"id": user_id},
            new_doc={
                "hashed_password": user_password.get_password_hash(new_password),
                "is_force_change_password": force_change_password,
                "is_force_login": force_login,
            },
        )
        return is_updated

    @staticmethod
    async def create_new_user(
        new_user_data: UserCreateSchema,
        **kwargs,
    ) -> UserCreateSchemaOut:
        user_dict_data = new_user_data.dict(exclude_unset=True)
        user_dict_data.update(
            hashed_password=user_password.get_password_hash(new_user_data.password)
        )
        if kwargs:
            user_dict_data.update(kwargs)
        if user_dict_data.get("email"):
            user_dict_data["email_verified"] = True
        elif user_dict_data.get("mobile_number"):
            user_dict_data["phone_verified"] = True
        created = await users_crud.create(UserDBCreateModel(**user_dict_data))
        result = await users_crud.get_joined_user(target_id=created.id)
        return UserCreateSchemaOut(**result)

    async def register_new_user(
        self, new_user_data: AuthRegisterIn, **kwargs
    ) -> Response:
        user_dict_data = new_user_data.dict()
        user_dict_data.update(
            hashed_password=user_password.get_password_hash(new_user_data.password)
        )
        if kwargs:
            user_dict_data.update(kwargs)
        user = await user_controller.find_by_username(
            username=new_user_data.username, raise_exception=False
        )
        username_type = new_user_data.username["value_type"]
        if user:
            if username_type == USERNAME_IS_EMAIL and user.email_verified:
                raise UserRegisterEmailExists
            elif username_type == USERNAME_IS_PHONE and user.phone_verified:
                raise UserRegisterPhoneExists
            else:
                query_options = {
                    USERNAME_IS_EMAIL: {
                        USERNAME_IS_EMAIL: new_user_data.username["value"],
                        "email_verified": False,
                    },
                    USERNAME_IS_PHONE: {
                        USERNAME_IS_PHONE: new_user_data.username["value"],
                        "phone_verified": False,
                    },
                }
                await users_crud.update(
                    query_options[new_user_data.username["value_type"]],
                    {new_user_data.username["value_type"]: None},
                )
                created_user, _ = await users_crud.default_update_and_get(
                    dict(id=user.id), new_doc=user_dict_data
                )
        else:
            created_user = await users_crud.create(UserDBCreateModel(**user_dict_data))
        await otp.set_otp_and_send_message(
            user=created_user,
            otp_type=AuthOTPTypeEnum.email
            if username_type == USERNAME_IS_EMAIL
            else AuthOTPTypeEnum.sms,
            cache_key=new_user_data.username["value"],
            request_type=OtpRequestType.verification,
        )
        return Response(
            message=UserMessageEnum.register_new_user_and_sent_otp, detail=[]
        )

    async def register_new_user_and_login(
        self,
        new_user_data: AuthRegisterIn,
        **kwargs,
    ) -> AuthToken:
        user_dict_data = new_user_data.dict()
        user_dict_data.update(
            hashed_password=user_password.get_password_hash(new_user_data.password)
        )
        if kwargs:
            user_dict_data.update(kwargs)
        try:
            created_user = await users_crud.create(UserDBCreateModel(**user_dict_data))
        except DuplicateKeyError as e:
            raise UserRegisterEmailExists from e
        return await self.generate_token_for_user(created_user)

    async def generate_token_for_user(self, user):
        if not user.is_enable:
            raise UserIsDisabled
        if user.is_blocked:
            raise UserIsBlocked
        if user.user_status == UserStatus.pending:
            raise UserIsPending
        if user.user_status == UserStatus.rejected:
            raise UserIsRejected
        await users_crud.update(
            criteria={"id": user.id},
            new_doc={
                "login_datetime": datetime.now(timezone.utc),
                "last_login_datetime": user.login_datetime,
            },
            operator=UpdateOperatorsEnum.set_,
        )
        return await token.generate_token(user.id, user.role)

    @staticmethod
    async def get_all_users(
        pagination: Pagination,
        ordering: Ordering,
        criteria: dict = None,
    ) -> PaginatedResponse[List[UsersGetUserSubListOut]]:
        if not criteria:
            criteria = {}
        pipeline = [
            {"$match": criteria},
            {"$addFields": {"country": "$settings.country_code"}},
        ]
        return await pagination.paginate(
            crud=users_crud,
            list_item_model=UsersGetUserSubListOut,
            pipeline=pipeline,
            _sort=await ordering.get_ordering_criteria(),
        )

    @staticmethod
    async def get_single_user(
        target_user_id: SchemaID,
    ) -> UsersGetUserOut:
        criteria = {
            "id": target_user_id,
        }
        target_user = await users_crud.get_object(criteria=criteria)
        return UsersGetUserOut(
            **target_user.dict(),
        )

    @staticmethod
    async def user_activation(
        target_user_id: SchemaID,
    ) -> UsersActivationUserPatchOut:
        target_user = await users_crud.get_object(
            criteria={"id": target_user_id},
        )
        updated_target_user, _ = await users_crud.update_and_get(
            criteria={"id": target_user.id},
            new_doc={"is_enable": not target_user.is_enable},
        )
        return UsersActivationUserPatchOut(status=updated_target_user.is_enable)

    @staticmethod
    async def user_blocking(
        target_user_id: SchemaID,
    ) -> UsersBlockingUserPatchOut:
        target_user = await users_crud.get_object(
            criteria={"id": target_user_id},
        )
        updated_target_user, _ = await users_crud.update_and_get(
            criteria={"id": target_user.id},
            new_doc={"is_blocked": not target_user.is_blocked},
        )
        return UsersBlockingUserPatchOut(status=updated_target_user.is_blocked)

    async def update_single_user(
        self,
        current_user: UserDBReadModel,
        new_data: UsersUpdateUserIn,
        target_id: SchemaID,
    ):
        is_updated, updated_user = await users_crud.update_user(
            current_user=current_user,
            new_data=new_data,
            target_id=target_id,
        )

        if not is_updated:
            raise UpdateFailed
        return UsersGetUserOut(
            **updated_user.dict(),
        )

    @staticmethod
    async def soft_delete_single_user(
        target_user_id: SchemaID,
    ) -> bool:
        target_user = await users_crud.get_object(
            criteria={"id": target_user_id},
        )
        is_deleted = await users_crud.soft_delete_by_id(_id=target_user_id)
        if target_user and is_deleted:
            return is_deleted
        else:
            raise DeleteFailed

    async def bulk_update_obj(
        self,
        obj_ids: List[SchemaID],
        new_obj_data: user_schema.UsersUpdateUserIn,
    ) -> List[UserDBReadModel]:
        data_dict = new_obj_data.dict(exclude_none=True)
        if data_dict.get("password"):
            data_dict["hashed_password"] = user_password.get_password_hash(
                new_obj_data.password
            )
        new_obj_dict = UserDBUpdateModel(**data_dict).dict(exclude_none=True)
        criteria = {"id": {"$in": obj_ids}}
        (
            updated_users,
            is_updated,
        ) = await self.crud.default_update_many_and_get(
            criteria=criteria, new_doc=new_obj_dict
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return updated_users

    async def bulk_delete_admins(
        self, obj_ids: List[SchemaID]
    ) -> List[UserDBReadModel]:
        return await users_crud.bulk_soft_delete(obj_ids=obj_ids)

    async def bulk_delete_customers(
        self,
        obj_ids: List[SchemaID],
    ) -> List[UserDBReadModel]:
        return await users_crud.bulk_soft_delete(obj_ids=obj_ids)

    async def bulk_delete_audits(
        self,
        obj_ids: List[SchemaID],
    ) -> List[UserDBReadModel]:
        return await users_crud.bulk_soft_delete(obj_ids=obj_ids)

    async def get_all_customers(
        self,
        pagination: Pagination,
        ordering: Ordering,
        criteria: dict = None,
    ) -> PaginatedResponse[List[UsersGetCustomerSubListOut]]:
        if not criteria:
            criteria = {}
        pipeline = [
            {"$match": criteria},
            {
                "$addFields": {
                    "country": "$settings.country_code",
                }
            },
        ]
        return await pagination.paginate(
            crud=users_crud,
            list_item_model=user_schema.UsersGetCustomerSubListOut,
            pipeline=pipeline,
            _sort=await ordering.get_ordering_criteria(),
        )

    async def add_new_device(
        self,
        request_payload: AddNewDeviceIn,
        current_user: UserDBReadModel,
        background_tasks: BackgroundTasks,
        user_agent: Optional[str],
    ):
        parsed_user_agent = user_agents.parse(user_agent)
        device_details = DeviceDetail(
            ua_string=parsed_user_agent.ua_string,
            os=parsed_user_agent.get_os(),
            browser=parsed_user_agent.get_browser(),
            device=parsed_user_agent.get_device(),
        )
        user_device = UserDevicesModel(
            **request_payload.dict(), device_detail=device_details
        ).dict(exclude_none=True)
        background_tasks.add_task(
            func=subscribe_to_topic,
            tokens=[request_payload.notification_token],
            topic=current_user.role.value,
        )
        background_tasks.add_task(
            func=subscribe_to_topic,
            tokens=[request_payload.notification_token],
            topic=request_payload.device_type,
        )
        return await users_crud.update(
            criteria={"id": current_user.id},
            new_doc={"devices": user_device},
            operator=UpdateOperatorsEnum.add_To_set_,
        )

    async def customer_register(
        self, payload: CustomerVerifyLoginOTPIn
    ) -> UserDBReadModel:
        new_user = payload.dict()
        username_type = payload.username["value_type"]
        if username_type == USERNAME_IS_EMAIL:
            new_user["email_verified"] = True
        elif username_type == USERNAME_IS_PHONE:
            new_user["phone_verified"] = True
        return await self.crud.create(
            UserDBCreateModel(
                **new_user,
                role=RoleEnum.customer.value,
                groups=[DefaultGroupNameEnum.customer.value],
                business_type=BusinessTypeEnum.PERSONAL.value,
            ),
        )

    async def audit_update_user(
        self, current_user: UserDBReadModel, payload: AuditUpdateUserIn, criteria: dict
    ):
        user = await self.crud.get_an_object(criteria=criteria)
        new_doc = payload.dict()
        if payload.is_blocked is True:
            new_doc["block_info"] = BlockInfoModel(
                **new_doc.get("block_reason"), blocked_by=current_user.id
            )
        new_doc = user.copy(update=new_doc).dict()
        result, is_updated = await self.crud.default_update_and_get(
            criteria={"id": user.id}, new_doc=new_doc
        )
        return result


user_controller = UserController(crud=users_crud)


class ProfileController(BaseController):
    async def get_my_profile(
        self, current_user: UserDBReadModel
    ) -> user_schema.ProfileGetMeOut:
        users_info = await users_crud.get_joined_user(current_user.id)
        return user_schema.ProfileGetMeOut(**users_info)

    async def update_my_profile(
        self,
        current_user: UserDBReadModel,
        payload: user_schema.ProfileUpdateMeIn,
    ) -> user_schema.ProfileGetMeOut:
        tasks = [
            users_crud.update_user(
                current_user=current_user,
                new_data=payload,
                target_id=current_user.id,
            ),
        ]
        if current_user.avatar:
            tasks.append(global_services.S3.get_presigned_url(current_user.avatar))
        (
            (is_updated, updated_user),
            *_,
        ) = await asyncio.gather(*tasks)
        if not is_updated:
            raise exceptions.UpdateFailed
        return user_schema.ProfileGetMeOut(
            **updated_user.dict(),
        )

    async def upload_avatar(
        self,
        avatar: ValidatedFile,
        current_user: Optional[UserDBReadModel] = None,
        user_id: Optional[SchemaID] = None,
    ) -> FileOut:
        _, extention = os.path.splitext(avatar.file_name)
        user_id = user_id or current_user.id
        avatar = await files_crud.upload_file_to_public_s3(avatar, extention)

        await users_crud.update(
            criteria={"id": user_id}, new_doc={"avatar": avatar.file_url}, upsert=False
        )
        return avatar

    async def delete_avatar(self, current_user: UserDBReadModel):
        if current_user.avatar:
            key = current_user.avatar.split("/")[-1]
            await global_services.S3.remove_object(key)
            await users_crud.update(
                criteria={"id": current_user.id}, new_doc={"avatar": None}
            )

    async def update_profile(
        self,
        current_user: UserDBReadModel,
        payload: user_schema.ProfileUpdateMeIn,
    ) -> user_schema.ProfileGetMeOut:
        is_updated, updated_user = await users_crud.update_user(
            current_user=current_user,
            new_data=payload,
            target_id=current_user.id,
        )
        if not is_updated and updated_user:
            raise exceptions.UpdateFailed
        return await self.get_my_profile(current_user=current_user)

    async def get_all_addresses(
        self, current_user: UserDBReadModel
    ) -> List[user_schema.AddressSchemaOut]:
        result = await users_crud.get_object(criteria=dict(id=current_user.id))
        return result.addresses

    async def create_new_address(
        self, current_user: UserDBReadModel, payload: user_schema.AddressSchemaIn
    ) -> List[user_schema.AddressSchemaOut]:
        if payload.is_default:
            is_updated = await users_crud.update(
                criteria={"id": current_user.id},
                new_doc={"addresses.$[].is_default": False},
            )
            if not is_updated:
                raise exceptions.UpdateFailed
        payload = payload.dict()
        payload.update({"address_id": str(uuid4())})
        user, is_updated = await users_crud.update_and_get(
            criteria={"id": current_user.id},
            new_doc={"addresses": payload},
            operator=UpdateOperatorsEnum.push_,
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return [
            user_schema.AddressSchemaOut(**address.dict()) for address in user.addresses
        ]

    async def get_single_address(
        self,
        current_user: UserDBReadModel,
        address_id: SchemaID,
    ) -> user_schema.AddressSchemaOut:
        result = await users_crud.get_object(
            criteria={"id": current_user.id, "addresses.address_id": address_id},
            projection={"addresses.$": 1},
        )
        return result.get("addresses")[0]

    async def update_single_address(
        self,
        current_user: UserDBReadModel,
        address_id: SchemaID,
        payload: user_schema.AddressSchemaIn,
    ) -> user_schema.AddressSchemaOut:
        if payload.is_default:
            is_updated = await users_crud.update(
                criteria={"id": current_user.id},
                new_doc={"addresses.$[].is_default": False},
            )
            if not is_updated:
                raise exceptions.UpdateFailed
        payload = payload.dict()
        payload["address_id"] = address_id
        is_updated = await users_crud.update(
            criteria={"id": current_user.id, "addresses.address_id": address_id},
            new_doc={"addresses.$": payload},
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return user_schema.AddressSchemaOut(**payload)

    async def delete_single_address(
        self, current_user: UserDBReadModel, address_id: SchemaID
    ) -> List[user_schema.AddressSchemaOut]:
        user, is_updated = await users_crud.update_and_get(
            criteria={"id": current_user.id},
            operator=UpdateOperatorsEnum.pull_,
            new_doc={"addresses": {"address_id": address_id}},
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return [
            user_schema.AddressSchemaOut(**address.dict()) for address in user.addresses
        ]

    async def get_my_permissions(
        self, current_user: UserDBReadModel
    ) -> user_schema.ProfileGetPermssions:
        permissions_dict = await permissions_crud.get_permissions_dict(current_user)
        permissions = [
            PermissionModel(entity=entity, rules=rules)
            for entity, rules in permissions_dict.items()
        ]
        return user_schema.ProfileGetPermssions(permissions=permissions)

    async def get_my_permissions_dict(
        self, current_user: UserDBReadModel
    ) -> user_schema.ProfileGetPermssionsDict:
        permissions_dict = await permissions_crud.get_permissions_dict(current_user)
        return user_schema.ProfileGetPermssionsDict(permissions=permissions_dict)


profile_controller = ProfileController(crud=users_crud)


class SavedBankCardsCrudController(BaseController):
    pass
