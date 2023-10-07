import re
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    Path,
    Query,
    Security,
    BackgroundTasks,
    responses,
)
from starlette import status
from starlette.responses import Response as StarletteResponse

from src.apps.auth.deps import get_admin_user, get_audit_user
from src.apps.file.schema import FileOut
from src.apps.language.enum import LanguageEnum
from src.apps.log_app.controller import log_controller
from src.apps.log_app.enum import LogActionEnum
from src.apps.user import schema as user_schema
from src.apps.user.controller import user_controller, profile_controller
from src.apps.user.crud import users_crud
from src.apps.user.enum import (
    ALL_USER_STATUSES,
    UserMessageEnum,
    UserStatus,
    BusinessTypeEnum,
)
from src.apps.user.models import UserDBReadModel
from src.apps.user.schema import CreateUserGroupEnum, UserCreateSchema
from src.core.base.messages import CommonMessageEnum
from src.core.base.schema import (
    BulkDeleteIn,
    PaginatedResponse,
    Response,
    CommonExportCsvSchemaOut,
)
from src.core.common.enums import RoleEnum, ALL_ROLES
from src.core.mixins import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import (
    common_responses,
    response_404,
    response_413,
)
from src.core.utils import return_on_failure
from src.core.validators import avatar_validation
from src.main.config import app_settings, collections_names
from src.main.enums import (
    ALL_COUNTRY_CODES,
    CountryCode,
)

user_router = APIRouter()
entity = collections_names.USERS


@user_router.get(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[
        PaginatedResponse[List[user_schema.UsersGetUserSubListOut]]
    ],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_all_users(
    _: UserDBReadModel = Security(get_admin_user, scopes=[entity, "list"]),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
) -> Response[PaginatedResponse[List[user_schema.UsersGetUserSubListOut]]]:
    criteria = {"is_deleted": False}
    result_data = await user_controller.get_all_users(
        pagination=pagination,
        ordering=ordering,
        criteria=criteria,
    )
    return Response[PaginatedResponse[List[user_schema.UsersGetUserSubListOut]]](
        data=result_data.dict()
    )


@user_router.get(
    "/export-csv",
    responses={
        **common_responses,
    },
    response_model=Response[CommonExportCsvSchemaOut],
    description="export CSV",
)
@return_on_failure
async def export_users_csv(
    _: UserDBReadModel = Security(get_admin_user, scopes=[entity, "list"]),
    search: Optional[str] = Query(None),
    user_status: Optional[List[UserStatus]] = Query(None, enum=ALL_USER_STATUSES),
    roles: Optional[List[RoleEnum]] = Query(None, enum=ALL_ROLES),
    groups: Optional[List[str]] = Query(None),
    country: Optional[List[CountryCode]] = Query(None, enum=ALL_COUNTRY_CODES),
):
    criteria = {"is_deleted": False}
    if search:
        criteria["$or"] = [
            {"first_name": re.compile(search, re.IGNORECASE)},
            {"last_name": re.compile(search, re.IGNORECASE)},
            {"email": re.compile(search, re.IGNORECASE)},
            {"mobile_number": re.compile(search, re.IGNORECASE)},
        ]
    if user_status:
        criteria["status"] = {"$in": user_status}
    if roles:
        criteria["role"] = {"$in": roles}
    if groups:
        criteria["groups"] = {"$in": groups}
    if country:
        criteria["settings.country"] = {"$in": country}
    result_data = await user_controller.export_csv(
        files_path=app_settings.DEFAULT_FILES_PATH,
        entity_name=entity,
        criteria=criteria,
    )
    return Response[CommonExportCsvSchemaOut](
        data=result_data.dict(), message=CommonMessageEnum.export_csv
    )


@user_router.post(
    "",
    status_code=201,
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.UsersCreateOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def create_new_user(
    background_tasks: BackgroundTasks,
    payload: user_schema.UserCreateSchema,
    current_user: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "create"],
    ),
) -> Response[user_schema.UsersCreateOut]:
    result_data = await user_controller.create_new_user(new_user_data=payload)
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.delete,
        action_by=current_user.id,
        entity=entity,
        entity_id=result_data.id,
    )
    return Response[user_schema.UsersCreateOut](data=result_data)


@user_router.post(
    "/admins/",
    status_code=201,
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.UsersCreateAdminOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def create_new_admin(
    payload: user_schema.UsersCreateAdminIn,
    # current_user: UserDBReadModel = Security(
    #     get_admin_user,
    #     scopes=[entity, "create"],
    # ),
):
    result_data = await user_controller.create_new_user(
        new_user_data=UserCreateSchema(
            **payload.dict(exclude_none=True),
            groups=[CreateUserGroupEnum.admin.value],
        ),
        role=RoleEnum.admin.value,
    )
    return Response[user_schema.UsersCreateAdminOut](data=result_data)


@user_router.post(
    "/customers",
    status_code=201,
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.UsersCreateAdminOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def create_new_customer(
    background_tasks: BackgroundTasks,
    payload: user_schema.UserCreateAdminCustomerIn,
    current_user: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "create"],
    ),
):
    result_data = await user_controller.create_new_user(
        new_user_data=UserCreateSchema(
            **payload.dict(exclude_none=True),
            groups=[CreateUserGroupEnum.customer.value],
        ),
        role=RoleEnum.customer.value,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.insert,
        action_by=current_user.id,
        entity=entity,
        entity_id=result_data.id,
    )
    return Response[user_schema.UsersCreateAdminOut](data=result_data)


@user_router.get(
    "/admins/",
    responses={
        **common_responses,
    },
    response_model=Response[
        PaginatedResponse[List[user_schema.UsersGetUserSubListOut]]
    ],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_all_admins(
    _: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "list"],
    ),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
) -> Response[PaginatedResponse[List[user_schema.UsersGetUserSubListOut]]]:
    criteria = {"role": RoleEnum.admin}
    result_data = await user_controller.get_all_users(
        pagination=pagination,
        ordering=ordering,
        criteria=criteria,
    )
    return Response[PaginatedResponse[List[user_schema.UsersGetUserSubListOut]]](
        data=result_data.dict()
    )


@user_router.get(
    "/customers",
    responses={
        **common_responses,
    },
    response_model=Response[
        PaginatedResponse[List[user_schema.UsersGetCustomerSubListOut]]
    ],
    description="By `Hamze.zn`",
)
@return_on_failure
async def admin_get_all_customers(
    _: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "list"],
    ),
    search: Optional[str] = Query(None),
    is_blocked: bool = Query(False),
    user_status: Optional[List[UserStatus]] = Query(None, enum=ALL_USER_STATUSES),
    business_type: List[BusinessTypeEnum] = Query(None),
    country: Optional[List[CountryCode]] = Query(None, enum=ALL_COUNTRY_CODES),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
) -> Response[PaginatedResponse[List[user_schema.UsersGetCustomerSubListOut]]]:
    criteria = {
        "role": RoleEnum.customer,
        "is_deleted": False,
        "is_blocked": is_blocked,
    }
    if search:
        criteria["$or"] = [
            {"first_name": re.compile(search, re.IGNORECASE)},
            {"last_name": re.compile(search, re.IGNORECASE)},
            {"email": re.compile(search, re.IGNORECASE)},
            {"mobile_number": re.compile(search, re.IGNORECASE)},
        ]
    if user_status:
        criteria["status"] = {"$in": user_status}
    if country:
        criteria["settings.country"] = {"$in": country}
    if business_type:
        criteria["business_type"] = {"$in": business_type}
    result_data = await user_controller.get_all_customers(
        pagination=pagination,
        ordering=ordering,
        criteria=criteria,
    )
    return Response[PaginatedResponse[List[user_schema.UsersGetCustomerSubListOut]]](
        data=result_data.dict()
    )


@user_router.get(
    "",
    responses={
        **common_responses,
    },
    response_model=Response[
        PaginatedResponse[List[user_schema.AuditGetUsersListSchema]]
    ],
    description="By `HamzeZN`",
)
@return_on_failure
async def get_all_customers(
    _: UserDBReadModel = Security(get_audit_user, scopes=[entity, "list"]),
    search: str = Query(None),
    is_blocked: bool = Query(False),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    criteria = {
        "role": RoleEnum.customer,
        "is_deleted": False,
        "is_blocked": is_blocked,
    }
    if search:
        criteria["$or"] = [
            {"first_name": re.compile(search, re.IGNORECASE)},
            {"last_name": re.compile(search, re.IGNORECASE)},
            {"email": re.compile(search, re.IGNORECASE)},
            {"mobile_number": re.compile(search, re.IGNORECASE)},
        ]
    result_data = await user_controller.get_all_customers(
        pagination=pagination,
        ordering=ordering,
        criteria=criteria,
    )
    return Response[PaginatedResponse[List[user_schema.AuditGetUsersListSchema]]](
        data=result_data.dict()
    )


@user_router.post(
    "/audits",
    status_code=201,
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.UsersCreateAdminOut],
    description="By `HamzeZN`",
)
@return_on_failure
async def create_new_audit(
    payload: user_schema.UsersCreateAdminIn,
    _: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "create"],
    ),
):
    result_data = await user_controller.create_new_user(
        new_user_data=UserCreateSchema(
            **payload.dict(exclude_none=True),
            groups=[CreateUserGroupEnum.audit.value],
        ),
        role=RoleEnum.audit.value,
    )
    return Response[user_schema.UsersCreateAdminOut](data=result_data)


@user_router.get(
    "/audits",
    responses={
        **common_responses,
    },
    response_model=Response[
        PaginatedResponse[List[user_schema.UsersGetUserSubListOut]]
    ],
    description="By `HamzeZN`do",
)
@return_on_failure
async def get_all_audits(
    _: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "list"],
    ),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
    is_blocked: bool = Query(False),
    search: str = Query(None),
) -> Response[PaginatedResponse[List[user_schema.UsersGetUserSubListOut]]]:
    criteria = {"role": RoleEnum.audit, "is_blocked": is_blocked}
    if search:
        criteria["$or"] = [
            {"first_name": re.compile(search, re.IGNORECASE)},
            {"last_name": re.compile(search, re.IGNORECASE)},
            {"email": re.compile(search, re.IGNORECASE)},
            {"mobile_number": re.compile(search, re.IGNORECASE)},
        ]
    result_data = await user_controller.get_all_users(
        pagination=pagination,
        ordering=ordering,
        criteria=criteria,
    )
    return Response[PaginatedResponse[List[user_schema.UsersGetUserSubListOut]]](
        data=result_data.dict()
    )


@user_router.get(
    "/{user_id}",
    responses={**common_responses},
    response_model=Response[user_schema.AuditGetUserDetailSchema],
    description="By `HamzeZN`",
)
@return_on_failure
async def get_single_user(
    user_id: SchemaID = Path(...),
    _: UserDBReadModel = Security(get_audit_user, scopes=[entity, "read"]),
):
    await users_crud.get_by_id(
        _id=user_id,
        criteria=dict(role=RoleEnum.customer.value),
        raise_exception=True,
    )
    result_data = await user_controller.get_single_user(target_user_id=user_id)
    return Response[user_schema.AuditGetUserDetailSchema](data=result_data)


@user_router.get(
    "/{user_id}/",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.UsersGetUserOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def admin_get_single_user(
    user_id: SchemaID = Path(...),
    _: UserDBReadModel = Security(get_admin_user, scopes=[entity, "read"]),
) -> Response[user_schema.UsersGetUserOut]:
    result_data = await user_controller.get_single_user(target_user_id=user_id)
    return Response[user_schema.UsersGetUserOut](data=result_data)


@user_router.get(
    "/admins/{user_id}/",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.UsersGetUserOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_single_admin(
    user_id: SchemaID = Path(...),
    _: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "read"],
    ),
) -> Response[user_schema.UsersGetUserOut]:
    await users_crud.get_by_id(
        _id=user_id,
        criteria=dict(role=RoleEnum.admin.value),
        raise_exception=True,
    )
    result_data = await user_controller.get_single_user(target_user_id=user_id)
    return Response[user_schema.UsersGetUserOut](data=result_data)


@user_router.get(
    "/customers/{user_id}/",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.UsersGetUserOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def get_single_customer(
    user_id: SchemaID = Path(...),
    _: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "read"],
    ),
) -> Response[user_schema.UsersGetUserOut]:
    await users_crud.get_by_id(
        _id=user_id,
        criteria=dict(role=RoleEnum.customer.value),
        raise_exception=True,
    )
    result_data = await user_controller.get_single_user(target_user_id=user_id)
    return Response[user_schema.UsersGetUserOut](data=result_data)


@user_router.patch(
    "/{user_id}",
    responses={**common_responses},
    status_code=200,
    response_model=Response[user_schema.UsersGetUserOut],
    description="By `HamzeZN`",
)
@return_on_failure
async def audit_update_single_user(
    payload: user_schema.AuditUpdateUserIn,
    background_tasks: BackgroundTasks,
    user_id: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(get_audit_user, scopes=[entity, "update"]),
):
    criteria = {"id": user_id, "role": RoleEnum.customer}
    result = await user_controller.audit_update_user(
        current_user=current_user, criteria=criteria, payload=payload
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=user_id,
        meta=payload.dict(include={"is_blocked"}),
        description=payload.block_reason.description if payload.block_reason else None,
    )
    return Response[user_schema.UsersGetUserOut](data=result)


@user_router.patch(
    "/{user_id}/",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.UsersGetUserOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def admin_update_single_user(
    background_tasks: BackgroundTasks,
    payload: user_schema.UsersUpdateUserIn,
    user_id: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "update"],
    ),
) -> Response[user_schema.UsersGetUserOut]:
    result_data = await user_controller.update_single_user(
        current_user=current_user,
        target_id=user_id,
        new_data=payload,
    )

    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=user_id,
    )
    return Response[user_schema.UsersGetUserOut](data=result_data)


async def users_bulk_update_method(
    background_tasks: BackgroundTasks,
    payload: user_schema.UserBulkUpdateIn,
    current_user: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "update"],
    ),
):
    result_data = await user_controller.bulk_update_obj(
        obj_ids=payload.ids, new_obj_data=payload
    )
    background_tasks.add_task(
        func=log_controller.bulk_create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_ids=payload.ids,
    )
    return Response[List[user_schema.UsersGetUserOut]](data=result_data)


@user_router.patch(
    "",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[List[user_schema.UsersGetUserOut]],
    description="By `Hamze.zn`",
)
@return_on_failure
async def bulk_update_users(
    background_tasks: BackgroundTasks,
    payload: user_schema.UserBulkUpdateIn,
    current_user: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "update"],
    ),
):
    return await users_bulk_update_method(background_tasks, payload, current_user)


@user_router.patch(
    "/admins/{user_id}/",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.UsersGetUserOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def update_single_admin(
    background_tasks: BackgroundTasks,
    payload: user_schema.UsersUpdateAdminUserIn,
    user_id: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "update"],
    ),
) -> Response[user_schema.UsersGetUserOut]:
    await users_crud.get_by_id(
        _id=user_id,
        criteria=dict(role=RoleEnum.admin.value),
        raise_exception=True,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=user_id,
    )
    result_data = await user_controller.update_single_user(
        current_user=current_user,
        target_id=user_id,
        new_data=payload,
    )
    return Response[user_schema.UsersGetUserOut](data=result_data)


@user_router.patch(
    "/admins",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[List[user_schema.UsersGetUserOut]],
    description="By `Hamze.zn`",
)
@return_on_failure
async def bulk_update_admins(
    background_tasks: BackgroundTasks,
    payload: user_schema.UserBulkUpdateIn,
    current_user: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "update"],
    ),
):
    return await users_bulk_update_method(background_tasks, payload, current_user)


@user_router.delete(
    "/admins",
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def bulk_delete_admins(
    background_tasks: BackgroundTasks,
    payload: BulkDeleteIn,
    current_user: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "delete"],
    ),
):
    await user_controller.bulk_delete_admins(obj_ids=payload.ids)
    background_tasks.add_task(
        func=log_controller.bulk_create_log,
        action=LogActionEnum.delete,
        action_by=current_user.id,
        entity=entity,
        entity_ids=payload.ids,
    )
    return StarletteResponse(status_code=204)


@user_router.patch(
    "/customers/{user_id}/",
    responses={
        **common_responses,
    },
    response_model=Response[user_schema.UsersGetUserOut],
    description="By `Hamze.zn`",
)
@return_on_failure
async def update_single_customer(
    background_tasks: BackgroundTasks,
    payload: user_schema.UsersUpdateAdminUserIn,
    user_id: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "update"],
    ),
) -> Response[user_schema.UsersGetUserOut]:
    await users_crud.get_by_id(
        _id=user_id,
        criteria=dict(role=RoleEnum.customer.value),
        raise_exception=True,
    )
    result_data = await user_controller.update_single_user(
        current_user=current_user,
        target_id=user_id,
        new_data=payload,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=user_id,
    )
    return Response[user_schema.UsersGetUserOut](data=result_data)


@user_router.patch(
    "/customers",
    responses={
        **common_responses,
        **response_404,
    },
    response_model=Response[List[user_schema.UsersGetUserOut]],
    description="By `Hamze.zn`",
)
@return_on_failure
async def bulk_update_customers(
    background_tasks: BackgroundTasks,
    payload: user_schema.UserBulkUpdateIn,
    current_user: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "update"],
    ),
):
    return await users_bulk_update_method(background_tasks, payload, current_user)


@user_router.delete(
    "/customers",
    responses={
        **common_responses,
        **response_404,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def bulk_delete_customers(
    background_tasks: BackgroundTasks,
    payload: BulkDeleteIn,
    current_user: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "delete"],
    ),
):
    await user_controller.bulk_delete_customers(obj_ids=payload.ids)
    background_tasks.add_task(
        func=log_controller.bulk_create_log,
        action=LogActionEnum.delete,
        action_by=current_user.id,
        entity=entity,
        entity_ids=payload.ids,
    )
    return StarletteResponse(status_code=204)


@user_router.post(
    "/{user_id}/password/reset",
    description="Set new password for given user_id by admin \n\nBy `Hamze.zn`",
    responses={**common_responses},
    response_model=Response,
)
@return_on_failure
async def set_new_password(
    background_tasks: BackgroundTasks,
    user_id: SchemaID,
    payload: user_schema.UsersChangePasswordByAdminIn,
    current_user: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "change_password"],
    ),
):
    result_data = await user_controller.set_password(
        new_password=payload.new_password,
        user_id=user_id,
        force_change_password=True,
        force_login=True,
    )
    background_tasks.add_task(
        func=log_controller.create_log,
        action=LogActionEnum.update,
        action_by=current_user.id,
        entity=entity,
        entity_id=user_id,
        description={LanguageEnum.english: "set password"},
    )
    return Response(detail=result_data, message=UserMessageEnum.changed_password)


@user_router.delete(
    "/{user_id}/",
    status_code=204,
    responses={
        **common_responses,
    },
    description="By `Hamze.zn`",
)
@return_on_failure
async def delete_single_user(
    background_tasks: BackgroundTasks,
    user_id: SchemaID = Path(...),
    current_user: UserDBReadModel = Security(
        get_admin_user,
        scopes=[entity, "delete"],
    ),
):
    if await user_controller.soft_delete_single_user(
        target_user_id=user_id,
    ):
        background_tasks.add_task(
            func=log_controller.create_log,
            action=LogActionEnum.delete,
            action_by=current_user.id,
            entity=entity,
            entity_id=user_id,
        )
        return StarletteResponse(status_code=204)


@user_router.patch(
    "/avatar/{user_id}/",
    description="Upload avatar for an existing user",
    status_code=status.HTTP_200_OK,
    responses={**common_responses, **response_413},
    response_model=Response[FileOut],
)
@return_on_failure
async def upload_avatar(
    user_id: SchemaID = Path(...),
    avatar=Depends(avatar_validation),
    _: UserDBReadModel = Security(get_admin_user, scopes=[entity, "update"]),
):
    result = await profile_controller.upload_avatar(avatar=avatar, user_id=user_id)
    return Response[FileOut](data=result)
