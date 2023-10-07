from typing import List

from fastapi import APIRouter, status, Security
from fastapi import Depends

from src.apps.auth.deps import get_current_user
from src.apps.file import schema as file_schema
from src.apps.file.controller import file_controller
from src.apps.user.models import UserDBReadModel
from src.core.base.schema import Response
from src.core.responses import (
    common_responses,
    response_413,
)
from src.core.upload import S3, Local, Memory, FileData
from src.core.utils import return_on_failure
from src.main.config import collections_names, app_settings

s3 = S3(config={"extra-args": {"ACL": "public-read"}})
local = Local(config={"dest": app_settings.DEFAULT_FILES_PATH})
memory = Memory()

file_router = APIRouter()
entity = collections_names.FILES


@file_router.get(
    "/gallery",
    status_code=status.HTTP_200_OK,
    responses={
        **common_responses,
    },
    response_model=Response[List[file_schema.FileGetListOut]],
)
@return_on_failure
async def get_files():
    # criteria = {"file_category": FileCategoryEnum.gallery.value}
    result_data = await file_controller.get_list_objs_without_pagination(
        # criteria=criteria
    )
    return Response[List[file_schema.FileGetListOut]](data=result_data)


# @file_router.post(
#     "",
#     status_code=status.HTTP_200_OK,
#     responses={**common_responses, **response_413},
#     response_model=Response[file_schema.FileCreateOut],
# )
# @return_on_failure
# async def upload_file(
#     background_tasks: BackgroundTasks,
#     file=Depends(file_validation),
#     current_user: UserDBReadModel = Security(get_current_user),
#     guest_id: Optional[SchemaID] = Header(
#         default=None, example=default_id(), alias="guest-id"
#     ),
# ) -> Response[file_schema.FileCreateOut]:
#     path = app_settings.DEFAULT_FILES_PATH
#     result = await file_controller.upload_file(
#         file=file,
#         path=path,
#         current_user=current_user,
#         background_tasks=background_tasks,
#         guest_id=guest_id,
#     )
#     return Response[file_schema.FileCreateOut](data=result)
#


@file_router.post(
    "",
    status_code=status.HTTP_200_OK,
    responses={**common_responses, **response_413},
    response_model=Response[file_schema.FileCreateOut],
)
async def local_upload(
    files: list[FileData] | FileData = Depends(local),
    _: UserDBReadModel = Security(get_current_user),
) -> Response[file_schema.FileCreateOut]:
    result = file_schema.FileCreateOut(
        file_url=str(files.path),
        thumbnail_url=str(files.path),
        file_type=files.content_type,
        file_name=files.filename,
    )
    return Response[file_schema.FileCreateOut](data=result)


# @file_router.post("/s3_upload", name="s3_upload")
# async def s3_upload(file: FileData = Depends(s3)) -> FileData:
#     return file
#
#
# @file_router.post("/memory_upload", name="memory_upload")
# async def memory_upload(file: FileData = Depends(memory)) -> FileData:
#     return file
