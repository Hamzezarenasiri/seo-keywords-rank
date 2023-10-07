from datetime import datetime
from enum import Enum
from typing import List, Optional, Type, TypeVar

import bson
from datetime import timezone
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from pymongo.client_session import ClientSession
from pymongo.collation import Collation
from pymongo.errors import DuplicateKeyError

from src.core.base.schema import BaseSchema
from src.core.common.exceptions import CustomHTTPException
from src.core.utils import CustomDict
from .base import BaseDB


class UpdateOperatorsEnum(str, Enum):
    set_: str = "$set"
    push_: str = "$push"
    pull_: str = "$pull"
    pop_: str = "$pop"
    add_To_set_: str = "$addToSet"
    inc: str = "$inc"


T = TypeVar("T", bound=BaseModel)


class MongoDB(BaseDB):
    """This class is the concrete implementation of MongoDB database."""

    T = TypeVar("T", bound=BaseModel)
    T_SCHEMA = TypeVar("T_SCHEMA", bound=BaseSchema)

    def __init__(self):
        self._client = None
        self._db = None

    async def connect(
        self,
        uri: str,
        connection_timeout: int,
        min_pool_size: int,
        max_pool_size: int,
    ):
        self._client = AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=connection_timeout,
            minPoolSize=min_pool_size,
            maxPoolSize=max_pool_size,
        )

    def sync_connect(
        self,
        uri: str,
        connection_timeout: int,
        min_pool_size: int,
        max_pool_size: int,
    ):
        self._client = AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=connection_timeout,
            minPoolSize=min_pool_size,
            maxPoolSize=max_pool_size,
        )

    async def get_database(self, database_name: str):
        self._db = self._client.get_database(
            database_name,
            codec_options=bson.codec_options.CodecOptions(
                uuid_representation=bson.binary.UUID_SUBTYPE
            ),
        )

    def sync_get_database(self, database_name: str):
        self._db = self._client.get_database(
            database_name,
            codec_options=bson.codec_options.CodecOptions(
                uuid_representation=bson.binary.UUID_SUBTYPE
            ),
        )

    async def disconnect(self):
        self._client.close()

    async def raw_count_filter(self, criteria: dict, model: Type[T], **kwargs) -> int:
        """
            return filtered items count
        example:
            count_filter(criteria={'name':'John'},table="user")

        :param model:
        :type model:
        :param criteria: filter
        :type criteria: dict
        :return: filtered items count
        :rtype: int
        """
        return await self._db[model.Meta.collection_name].count_documents(
            criteria, **kwargs
        )

    async def raw_read_many(
        self,
        criteria: dict,
        model: Type[T],
        sort: list = None,
        skip: int = 0,
        limit: int = 0,
        projection: Optional[dict] = None,
    ) -> Optional[List[T]]:
        return [
            model(**doc)
            async for doc in self._db[model.Meta.collection_name].find(
                criteria, sort=sort, skip=skip, limit=limit, projection=projection
            )
        ]

    async def raw_read_one(
        self,
        criteria: dict,
        model: Type[T],
        projection: Optional[dict] = None,
        *args,
        **kwargs,
    ) -> Optional[T]:
        document = (
            await self._db[model.Meta.collection_name].find_one(
                criteria,
                projection,
                *args,
                **kwargs,
            )
        ) or None
        return model(**document) if document else None

    async def raw_exists(
        self,
        criteria: dict,
        model: Type[T],
        projection: Optional[dict] = None,
        *args,
        **kwargs,
    ) -> Optional[bool]:
        document = (
            await self._db[model.Meta.collection_name].find_one(
                criteria,
                projection,
                *args,
                **kwargs,
            )
        ) or None
        return bool(document)

    async def raw_read_one_and_project(
        self,
        criteria: dict,
        model: Type[T],
        projection: Optional[dict] = None,
        *args,
        **kwargs,
    ) -> Optional[dict]:
        document = (
            await self._db[model.Meta.collection_name].find_one(
                criteria,
                projection,
                *args,
                **kwargs,
            )
        ) or None
        return document or None

    async def raw_aggregate(
        self, pipeline: List[dict], model: Type[T], **kwargs
    ) -> List[CustomDict]:
        return [
            CustomDict(doc)
            async for doc in self._db[model.Meta.collection_name].aggregate(
                pipeline, **kwargs
            )
        ]

    async def raw_aggregate_schema(
        self, pipeline: List[dict], schema: Type[T_SCHEMA], model: Type[T], **kwargs
    ) -> List[T_SCHEMA]:
        return [
            schema(**doc)
            async for doc in self._db[model.Meta.collection_name].aggregate(
                pipeline, **kwargs
            )
        ]

    async def raw_aggregate_cursor(
        self, pipeline: List[dict], model: Type[T], **kwargs
    ):
        return self._db[model.Meta.collection_name].aggregate(pipeline, **kwargs)

    async def raw_update(
        self,
        criteria: dict,
        model: Type[T],
        new_values: dict,
        operator: Optional[UpdateOperatorsEnum],
        upsert: Optional[bool] = False,
    ) -> bool:
        if operator == UpdateOperatorsEnum.set_:
            new_values |= dict(update_datetime=datetime.now(timezone.utc))
        if operator is not None:
            update_statement = {operator: new_values}
        else:
            new_values["$set"] = {"update_datetime": datetime.now(timezone.utc)}
            update_statement = new_values
        if upsert:
            update_statement["$setOnInsert"] = {
                "create_datetime": datetime.now(timezone.utc)
            }
        try:
            result = await self._db[model.Meta.collection_name].update_one(
                filter=criteria, update=update_statement, upsert=upsert
            )
        except DuplicateKeyError as e:
            key = list(e.details["keyValue"].keys())[0]
            raise CustomHTTPException(
                message=f"{key} value ({e.details['keyValue'][key]}) is duplicate and can not be updated",
                detail={
                    "loc": ["body", key],
                    "msg": "field duplicated",
                    "type": "value_error.duplicate",
                },
                status_code=409,
            ) from e
        return result.acknowledged

    async def raw_update_many(
        self,
        criteria: dict,
        new_values: dict,
        model: Type[T],
        operator: UpdateOperatorsEnum = UpdateOperatorsEnum.set_,
        upsert: Optional[bool] = False,
        bypass_document_validation: Optional[bool] = False,
        collation: Optional[Collation] = None,
        array_filters: Optional[List[dict]] = None,
        hint: Optional[List[tuple]] = None,
        session: Optional[ClientSession] = None,
    ) -> bool:
        if operator == UpdateOperatorsEnum.set_:
            new_values.update(dict(update_datetime=datetime.utcnow()))

        update_statement = {operator: new_values}
        if upsert:
            update_statement["$setOnInsert"] = {"create_datetime": datetime.utcnow()}
        result = await self._db[model.Meta.collection_name].update_many(
            filter=criteria,
            update=update_statement,
            upsert=upsert,
            bypass_document_validation=bypass_document_validation,
            collation=collation,
            array_filters=array_filters,
            hint=hint,
            session=session,
        )
        return result

    async def raw_insert(
        self, obj: Type[T], model: Type[T], read_model: Type[T]
    ) -> Optional[T]:
        try:
            result = await self._db[model.Meta.collection_name].insert_one(obj.dict())
        except DuplicateKeyError as e:
            key = list(e.details["keyValue"].keys())[0]
            raise CustomHTTPException(
                message=f"{key} value ({e.details['keyValue'][key]}) is duplicate and can not be inserted",
                detail={
                    "loc": ["body", key],
                    "msg": "field duplicated",
                    "type": "value_error.duplicate",
                },
                status_code=409,
            ) from e
        return await self.raw_read_one(
            criteria={"_id": result.inserted_id}, model=read_model
        )

    async def raw_insert_many(
        self, obj_list: List[Type[T]], model: Type[T], read_model: Type[T]
    ) -> Optional[T]:
        result = await self._db[model.Meta.collection_name].insert_many(
            [obj.dict() for obj in obj_list]
        )
        if result.inserted_ids:
            return await self.raw_read_many(
                criteria={"_id": result.inserted_ids}, model=read_model
            )
        return None

    async def raw_delete(
        self,
        criteria: dict,
        model: Type[T],
        *args,
        **kwargs,
    ) -> bool:
        return await self._db[model.Meta.collection_name].delete_one(
            filter=criteria, *args, **kwargs
        )

    async def raw_delete_many(
        self,
        criteria: dict,
        model: Type[T],
        *args,
        **kwargs,
    ):
        return await self._db[model.Meta.collection_name].delete_many(
            filter=criteria, *args, **kwargs
        )

    async def raw_distinct(
        self,
        field: str,
        model: Type[T],
        criteria: Optional[dict] = None,
        **kwargs,
    ) -> list:
        return await self._db[model.Meta.collection_name].distinct(
            key=field,
            filter=criteria,
            **kwargs,
        )

    async def bulk_write(
        self,
        requests,
        model: Type[T],
        **kwargs,
    ) -> list:
        return await self._db[model.Meta.collection_name].bulk_write(
            requests=requests,
            **kwargs,
        )

    async def create_indexes(self, model: Type[T], **kwargs):
        if indexes := getattr(model.Meta, "indexes", None):
            return await self._db[model.Meta.collection_name].create_indexes(
                indexes, **kwargs
            )
