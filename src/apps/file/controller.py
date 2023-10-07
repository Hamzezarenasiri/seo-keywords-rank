import os
from typing import List, Optional
from fastapi import BackgroundTasks

from src.apps.user.models import UserDBReadModel
from src.core.base.controller import BaseController
from src.core.base.schema import PaginatedResponse
from src.core.common import exceptions
from src.core.common.enums import RoleEnum
from src.core.mixins import SchemaID
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.main.config import app_settings
from . import schema as file_schema
from .crud import files_crud
from .exception import FileIsUsed


class FileController(BaseController):
    async def upload_file(
        self,
        file: file_schema.ValidatedFile,
        path: str,
        current_user: UserDBReadModel,
        meta_fields: Optional[file_schema.FileUploadDataIn] = None,
        file_id: str = None,
        background_tasks: Optional[BackgroundTasks] = None,
        guest_id: SchemaID = None,
    ) -> file_schema.FileCreateOut:
        """Receive a file object and the path then save it on server"""
        return await self.crud.save_file_meta(
            file=file,
            path=path,
            user_id=current_user.id if current_user else guest_id,
            meta_fields=meta_fields,
            file_id=file_id,
            background_tasks=background_tasks,
        )

    async def update_file_meta(
        self,
        file_id: SchemaID,
        file_meta: file_schema.FileUpdateIn,
        current_user: UserDBReadModel,
    ) -> file_schema.FileUpdateOut:
        """Receive a file meta like alt, save it on DB"""

        criteria = {"id": file_id, "user_id": current_user.id}
        if current_user.role == RoleEnum.admin.value:
            criteria = {"id": file_id}
        updated, is_updated = await self.crud.update_and_get(
            criteria=criteria,
            new_doc={**file_meta.dict()},
        )
        if not is_updated:
            raise exceptions.UpdateFailed
        return file_schema.FileUpdateOut(**updated.dict())

    async def soft_delete_files(
        self,
        obj_ids: List[SchemaID],
        current_user: UserDBReadModel,
    ):
        """Delete file meta recordd from DB"""
        criteria = {"id": {"$in": obj_ids}}
        if current_user.role != RoleEnum.admin.value:
            criteria["user_id"] = current_user.id
        target_file_metas = await self.crud.get_list(
            criteria=criteria,
        )
        for target_file_meta in target_file_metas:
            if target_file_meta.is_used:
                raise FileIsUsed
            original_file_path = (
                f"{app_settings.DEFAULT_FILES_PATH}"
                f"/original/{target_file_meta.file_name}"
            )
            thumbnail_file_path = (
                f"{app_settings.DEFAULT_FILES_PATH}"
                f"/thumbnail/{target_file_meta.file_name}"
            )
            if os.path.exists(original_file_path):
                os.remove(original_file_path)
            if os.path.exists(thumbnail_file_path):
                os.remove(thumbnail_file_path)
            is_deleted = await self.crud.soft_delete_by_id(
                _id=target_file_meta.id,
            )
            if not is_deleted:
                raise exceptions.DeleteFailed

    async def get_files(
        self,
        current_user: UserDBReadModel,
        pagination: Pagination,
        ordering: Ordering,
        search: Optional[str] = None,
        criteria: Optional[dict] = None,
    ) -> PaginatedResponse[List[file_schema.FileGetListOut]]:
        if criteria is None:
            criteria = {}
        criteria.update({"is_deleted": False})
        if current_user.role != RoleEnum.admin:
            criteria.update({"is_enable": True})
        if search:
            criteria.update({"file_name": {"$regex": f".*{search}.*"}})
        return await pagination.paginate(
            crud=self.crud,
            list_item_model=file_schema.FileGetListOut,
            criteria=criteria,
            _sort=await ordering.get_ordering_criteria(),
        )


file_controller = FileController(
    crud=files_crud,
    get_out_schema=file_schema.FileGetOut,
)
