import asyncio
from functools import cached_property
from base64 import b64encode, b64decode
from binascii import Error
from urllib import parse
from collections import namedtuple
from datetime import datetime
from typing import List, Optional, Tuple, Type, TypeVar, Union
from fastapi import Query
from pydantic import BaseModel
from starlette.requests import Request
from src.core.mixins.fields import PyObjectId
from src.core.base.crud import BaseCRUD
from src.core.base.schema import PaginatedResponse, CursorPaginatedResponse  # noqa
from src.core.common.exceptions import CustomHTTPException

ModelT = TypeVar("ModelT", bound=BaseModel)


class Pagination(object):
    default_offset = 0
    default_limit = 10
    max_offset = None
    max_limit = 500

    def __init__(
        self,
        request: Request,
        offset: int = Query(default=default_offset, ge=0, le=max_offset),
        limit: int = Query(default=default_limit, ge=1, le=max_limit),
    ):
        self.request = request
        self.offset = offset
        self.limit = limit
        self.crud = None
        self.list_item_model = None
        self.count = None
        self.list = []

    async def get_count(self, criteria: dict = None) -> int:
        if criteria is None:
            criteria = {}
        self.count = await self.crud.count(criteria=criteria)
        return self.count

    def get_next_url(self) -> Union[str, None]:
        if self.offset + self.limit >= self.count:
            return None
        return str(
            self.request.url.include_query_params(
                limit=self.limit,
                offset=self.offset + self.limit,
            )
        )

    def get_previous_url(self) -> Union[str, None]:
        if self.offset <= 0:
            return None

        if self.offset - self.limit <= 0:
            return str(self.request.url.remove_query_params(keys=["offset"]))

        return str(
            self.request.url.include_query_params(
                limit=self.limit,
                offset=self.offset - self.limit,
            )
        )

    async def get_list(self, criteria: dict = None, _sort=None) -> list:
        self.list = await self.crud.get_list(
            criteria=criteria,
            limit=self.limit,
            skip=self.offset,
            sort=_sort,
        )
        return self.list

    async def get_list_aggregate(
        self,
        pipeline: List[dict] = None,
        criteria: dict = None,
        _sort: dict = None,
        **kwargs,
    ) -> Tuple[List[dict], int]:
        if not pipeline:
            pipeline = []
        if criteria:
            pipeline.insert(0, {"$match": criteria})
        _list_pipeline = [
            {"$skip": self.offset},
            {"$limit": self.limit},
        ]
        if _sort:
            _list_pipeline.insert(0, {"$sort": _sort})
        paginate_pipe = [
            {
                "$facet": {
                    "_list": _list_pipeline,
                    "page_info": [
                        {"$group": {"_id": None, "count": {"$sum": 1}}},
                    ],
                },
            }
        ]
        pipeline += paginate_pipe
        result = (
            await self.crud.aggregate(
                pipeline=pipeline,
                **kwargs,
            )
        )[0]
        self.list = result["_list"]
        self.count = result["page_info"][0]["count"] if result["page_info"] else 0
        return self.list, self.count

    async def paginate(
        self,
        crud: BaseCRUD,
        list_item_model: Type[BaseModel],
        criteria: dict = None,
        pipeline: List[dict] = None,
        _sort: Optional[List[tuple]] = None,
        by_alias=True,
        **kwargs,
    ) -> PaginatedResponse[List[Type[ModelT]]]:
        self.crud = crud
        self.list_item_model = list_item_model
        if pipeline:
            if _sort and isinstance(_sort, List):
                _sort = dict(_sort)
            await self.get_list_aggregate(
                pipeline=pipeline,
                _sort=_sort,
                criteria=criteria,
                **kwargs,
            )
            items = [
                self.list_item_model(**item).dict(exclude_none=True, by_alias=by_alias)
                for item in self.list
            ]
        else:
            await asyncio.gather(
                self.get_list(criteria=criteria, _sort=_sort),
                self.get_count(criteria=criteria),
            )
            items = [
                self.list_item_model(**item.dict(exclude_none=True, by_alias=by_alias))
                for item in self.list
            ]
        return PaginatedResponse[List[list_item_model]](
            total=self.count,
            offset=self.offset,
            limit=self.limit,
            next=self.get_next_url(),
            previous=self.get_previous_url(),
            result=items,
        )


class Cursor(BaseModel):
    value: Optional[Union[PyObjectId, int, datetime]]
    is_reversed: int = 0

    class Config:
        smart_union = True


Ordering = namedtuple("Ordering", ["field", "is_descending"])


class CursorPagination:
    def __init__(
        self,
        limit: int = Query(default=10, ge=1, le=500),
        cursor: str = Query(None, description="next or previous cursor"),
    ):
        self._cursor = cursor
        self.limit = limit
        self.list_item_model = None
        self._ordering = None
        self.count = None
        self.crud = None
        self.list = []

    @property
    def next_cursor(self):
        if len(self.list) == self.limit:
            cursor_value = self._get_value_from_instance(
                self.list[-1], self.ordering.field
            )
            if self._cursor:
                current_cursor = self.decode_cursor(self._cursor)
                if current_cursor.is_reversed:
                    cursor_value = self._get_value_from_instance(
                        self.list[0], self.ordering.field
                    )
            return self.encode_cursor(Cursor(value=cursor_value))

    @property
    def previous_cursor(self):
        if self._cursor and self.list:
            cursor_value = self._get_value_from_instance(
                self.list[0], self.ordering.field
            )
            current_cursor = self.decode_cursor(self._cursor)
            if current_cursor.is_reversed:
                cursor_value = self._get_value_from_instance(
                    self.list[-1], self.ordering.field
                )
            return self.encode_cursor(Cursor(value=cursor_value, is_reversed=True))

    @cached_property
    def ordering(self):
        field, sort_type = self._sort[0]
        is_descending = True if sort_type == -1 else False
        return Ordering(field=field, is_descending=is_descending)

    def encode_cursor(self, cursor: Cursor) -> str:
        tokens = cursor.dict(exclude_none=True)
        query_string = parse.urlencode(tokens, doseq=True)
        return b64encode(query_string.encode("ascii"))

    def decode_cursor(self, cursor: str) -> Cursor:
        try:
            decoded = b64decode(cursor).decode("ascii")
            tokens = parse.parse_qs(decoded, keep_blank_values=True)
            value = tokens.get("value", [None])[0]
            is_reversed = int(tokens.get("is_reversed", ["0"])[0])
            return Cursor(value=value, is_reversed=is_reversed)
        except Error:
            raise CustomHTTPException(status_code=422, detail="invalid cursor")

    def reverse_sorting(self, sorts: list):
        # reverse the sort to get correct range on prev cursors
        reversed_sort = []
        for field, sort_type in sorts:
            sort_type = -1 if sort_type == 1 else 1
            reversed_sort.append((field, sort_type))
        return reversed_sort

    def _get_cursor_criteria(self, cursor: Cursor):
        if self.ordering.is_descending != bool(cursor.is_reversed):
            criteria = {self.ordering.field: {"$lt": cursor.value}}
        else:
            criteria = {self.ordering.field: {"$gt": cursor.value}}
        if cursor.is_reversed:
            self._sort = self.reverse_sorting(self._sort)
        return criteria

    def _get_value_from_instance(self, instance, field):
        if isinstance(instance, dict):
            return instance[field]
        return getattr(instance, field)

    async def get_list_aggregate(
        self,
        pipeline: List[dict] = None,
        criteria: dict = None,
        **kwargs,
    ) -> Tuple[List[dict], int]:
        criteria = criteria if criteria else {}
        if self._cursor:
            cursor = self.decode_cursor(self._cursor)
            criteria.update(self._get_cursor_criteria(cursor))
        if not pipeline:
            pipeline = []
        if criteria:
            pipeline.insert(0, {"$match": criteria})
        _list_pipeline = [
            {"$sort": dict(self._sort)},
            {"$limit": self.limit},
        ]
        paginate_pipe = [
            {
                "$facet": {
                    "_list": _list_pipeline,
                    "page_info": [
                        {"$group": {"_id": None, "count": {"$sum": 1}}},
                    ],
                },
            }
        ]
        pipeline += paginate_pipe
        result = (
            await self.crud.aggregate(
                pipeline=pipeline,
                **kwargs,
            )
        )[0]
        self.list = result["_list"]
        self.count = result["page_info"][0]["count"] if result["page_info"] else 0
        return self.list, self.count

    async def get_count(self, criteria: dict = None) -> int:
        if criteria is None:
            criteria = {}
        self.count = await self.crud.count(criteria=criteria)
        return self.count

    async def get_list(self, criteria: dict = None) -> list:
        criteria = criteria if criteria else {}
        criteria = {**criteria}
        if self._cursor:
            cursor = self.decode_cursor(self._cursor)
            criteria.update(self._get_cursor_criteria(cursor))
        self.list = await self.crud.get_list(
            criteria=criteria,
            limit=self.limit,
            sort=self._sort,
        )
        return self.list

    async def paginate(
        self,
        crud: BaseCRUD,
        _sort: List[tuple],
        list_item_model: Type[BaseModel],
        pipeline: List[dict] = None,
        criteria: dict = None,
        by_alias=True,
        **kwargs,
    ) -> dict:
        self.crud = crud
        self._sort = _sort
        self.list_item_model = list_item_model
        if pipeline:
            await self.get_list_aggregate(
                pipeline=pipeline,
                criteria=criteria,
                **kwargs,
            )
            items = [
                self.list_item_model(**item).dict(exclude_none=True, by_alias=by_alias)
                for item in self.list
            ]
        else:
            await asyncio.gather(
                self.get_list(criteria=criteria),
                self.get_count(criteria=criteria),
            )
            items = [
                self.list_item_model(**item.dict(exclude_none=True, by_alias=by_alias))
                for item in self.list
            ]
        return {
            "total": self.count,
            "next_cursor": self.next_cursor,
            "previous_cursor": self.previous_cursor,
            "result": items,
        }
