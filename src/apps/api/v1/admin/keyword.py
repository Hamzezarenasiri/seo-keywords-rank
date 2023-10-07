import re
from typing import List

import tldextract
from fastapi import APIRouter, Depends, Query, BackgroundTasks

from src.apps.keyword import schema as keyword_schemas
from src.apps.keyword.controller import keyword_controller
from src.core.base.schema import Response, PaginatedResponse
from src.core.ordering import Ordering
from src.core.pagination import Pagination
from src.core.responses import common_responses
from src.core.utils import return_on_failure
from src.main.config import collections_names

entity = collections_names.KEYWORDS
keyword_router = APIRouter()

# CELERY_BROKER_URL = config("CELERY_BROKER_URL")
# CELERY_BACKEND_URL = config("CELERY_BACKEND_URL")

# celery_client = Celery("client", broker=CELERY_BROKER_URL, backend=CELERY_BACKEND_URL)


@keyword_router.get(
    "",
    responses={**common_responses},
    response_model=Response[PaginatedResponse[List[keyword_schemas.KeywordListSchema]]],
    description="by `HamzeZN`",
)
@return_on_failure
async def admin_get_keyword(
    # _: UserDBReadModel = Security(get_admin_user, scopes=[entity, "list"]),
    keyword: None | str = Query(None),
    domain: None | str = Query(None),
    pagination: Pagination = Depends(),
    ordering: Ordering = Depends(Ordering()),
):
    criteria = {"is_deleted": False}
    if keyword:
        criteria["keyword"] = re.compile(keyword, re.IGNORECASE)
    if domain:
        criteria["domain"] = re.compile(domain, re.IGNORECASE)
    keyword = await keyword_controller.get_list_objs(
        pagination=pagination,
        ordering=ordering,
        criteria=criteria,
        sub_list_schema=keyword_schemas.KeywordListSchema,
    )
    return Response[PaginatedResponse[List[keyword_schemas.KeywordListSchema]]](
        data=keyword
    )


@keyword_router.post(
    "",
    responses={**common_responses},
    response_model=Response[keyword_schemas.KeywordDetailSchema],
    status_code=201,
    description="by `HamzeZN`",
)
@return_on_failure
async def admin_create_keyword(
    payload: keyword_schemas.KeywordCreateIn,
    background_tasks: BackgroundTasks,
    # current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "create"]),
):
    domain = tldextract.extract(payload.domain).registered_domain
    keyword = await keyword_controller.get_or_create_obj(
        criteria={"keyword": payload.keyword, "domain": domain}, new_data=payload
    )
    background_tasks.add_task(
        func=keyword_controller.get_and_update_rank,
        keyword=payload.keyword,
        domain=domain,
    )

    # celery_client.send_task(
    #     "src.celery.get_rank_task",
    #     kwargs={"keyword": payload.keyword, "domain": domain},
    # )
    # background_tasks.add_task(
    #     func=log_controller.create_log,
    #     action=LogActionEnum.insert,
    #     action_by=current_user.id,
    #     entity=entity,
    #     entity_id=keyword.id,
    # )
    return Response[keyword_schemas.KeywordDetailSchema](data=keyword)


@keyword_router.get(
    "/update_all_ranks",
    responses={**common_responses},
    response_model=Response,
    description="by `HamzeZN`",
)
@return_on_failure
async def update_all_ranks(
    # _: UserDBReadModel = Security(get_admin_user, scopes=[entity, "list"]),
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(func=keyword_controller.update_all_rank)
    # celery_client.send_task("src.celery.get_rank_daily_task")
    return Response(message="Ok - please wait ...")


# @keyword_router.get(
#     "/{keyword_id}",
#     responses={
#         **common_responses,
#         **response_404,
#     },
#     response_model=Response[keyword_schemas.KeywordDetailSchema],
#     description="by `HamzeZN`",
# )
# @return_on_failure
# async def admin_get_keyword(
#         keyword_id: SchemaID = Path(...),
#         _: UserDBReadModel = Security(get_admin_user, scopes=[entity, "read"]),
# ):
#     keyword = await keyword_controller.get_single_obj(keyword_id=keyword_id)
#     return Response[keyword_schemas.KeywordDetailSchema](data=keyword)
#
#
# @keyword_router.patch(
#     "/{keyword_id}",
#     responses={
#         **common_responses,
#         **response_404,
#     },
#     response_model=Response[keyword_schemas.KeywordDetailSchema],
#     description="by `HamzeZN`",
# )
# @return_on_failure
# async def admin_update_keyword(
#         payload: keyword_schemas.KeywordUpdateIn,
#         background_tasks: BackgroundTasks,
#         keyword_id: SchemaID = Path(...),
#         current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "update"]),
# ):
#     updated_keyword = await keyword_controller.update_single_obj(
#         criteria={"id": keyword_id}, new_data=payload
#     )
#     background_tasks.add_task(
#         func=log_controller.create_log,
#         action=LogActionEnum.update,
#         action_by=current_user.id,
#         entity=entity,
#         entity_id=updated_keyword.id,
#     )
#     return Response[keyword_schemas.KeywordDetailSchema](data=updated_keyword)
#
#
# @keyword_router.delete(
#     "/{keyword_id}",
#     responses={
#         **common_responses,
#         **response_404,
#     },
#     description="by `HamzeZN`",
#     status_code=204,
# )
# @return_on_failure
# async def admin_delete_keyword(
#         background_tasks: BackgroundTasks,
#         keyword_id: SchemaID = Path(...),
#         current_user: UserDBReadModel = Security(get_admin_user, scopes=[entity, "list"]),
# ):
#     keyword_id, city_ids = await keyword_controller.soft_delete_keyword(keyword_id=keyword_id)
#     background_tasks.add_task(
#         func=log_controller.create_log,
#         action=LogActionEnum.delete,
#         action_by=current_user.id,
#         entity=entity,
#         entity_id=keyword_id,
#     )
#     if city_ids:
#         background_tasks.add_task(
#             func=log_controller.bulk_create_log,
#             action=LogActionEnum.delete,
#             action_by=current_user.id,
#             entity=entity,
#             entity_ids=city_ids,
#         )
#     return responses.Response(status_code=204)
