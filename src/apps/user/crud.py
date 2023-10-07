from typing import Optional, Tuple

from src.apps.user.exception import AddressIDNotFound, UserNotFound
from src.apps.user.models import (
    UserDBCreateModel,
    UserDBReadModel,
    UserDBUpdateModel,
    AddressModel,
    BlockInfoModel,
)
from src.apps.user.schema import UsersUpdateUserIn
from src.core.base.crud import BaseCRUD
from src.core.mixins.fields import DB_ID, SchemaID
from src.core.security import user_password


class UserCRUD(BaseCRUD):
    async def update_user(
        self,
        current_user: UserDBReadModel,
        new_data: UsersUpdateUserIn,
        target_id: SchemaID,
    ) -> Tuple[bool, UserDBReadModel]:
        stored_item_model: UserDBReadModel = await self.get_by_id(target_id)
        data_dict = new_data.dict(exclude_unset=True)
        updated_item = stored_item_model.copy(update=data_dict).dict()
        if updated_item.get("password"):
            updated_item["hashed_password"] = user_password.get_password_hash(
                new_data.password
            )
        if data_dict.get("is_blocked"):
            updated_item["block_info"] = BlockInfoModel(
                **data_dict.get("block_reason"), blocked_by=current_user.id
            )
        updated_user, is_updated = await self.update_and_get(
            criteria={"id": target_id},
            new_doc=self.update_db_model(**updated_item).dict(),
        )

        return is_updated, updated_user

    async def get_joined_user(
        self,
        target_id: DB_ID,
        criteria: Optional[dict] = None,
    ) -> dict:
        if criteria is None:
            criteria = {}
        criteria.update({"id": target_id})
        pipeline = [{"$match": criteria}]
        result = await self.aggregate(pipeline=pipeline)
        if not result:
            raise UserNotFound
        return result[0]

    async def get_address(
        self,
        user_id: SchemaID,
        address_id: Optional[SchemaID] = None,
        raise_exception=True,
    ) -> Optional[AddressModel]:
        if address_id:
            condition = {
                "$eq": [
                    "$$addresses.address_id",
                    address_id,
                ]
            }
        else:
            condition = {
                "$eq": [
                    "$$addresses.is_default",
                    True,
                ]
            }
        pipeline = [
            {"$match": {"id": user_id}},
            {
                "$project": {
                    "details": {
                        "$filter": {
                            "input": "$addresses",
                            "as": "addresses",
                            "cond": condition,
                        }
                    }
                }
            },
            {"$unwind": "$details"},
        ]
        address = await self.aggregate(pipeline=pipeline)
        if raise_exception and (not address or not len(address[0]["details"])):
            raise AddressIDNotFound
        return AddressModel(**address[0]["details"]) if address else None

    async def get_address_by_address_id(
        self, address_id: SchemaID
    ) -> Optional[AddressModel]:
        pipeline = [
            {
                "$project": {
                    "details": {
                        "$filter": {
                            "input": "$addresses",
                            "as": "addresses",
                            "cond": {
                                "$eq": [
                                    "$$addresses.address_id",
                                    address_id,
                                ]
                            },
                        }
                    }
                }
            },
            {"$unwind": "$details"},
        ]
        address = await self.aggregate(pipeline=pipeline)
        return AddressModel(**address[0]["details"]) if address else None

    async def export_csv_join_aggregate(self, criteria):
        project = {
            "first_name": 1,
            "last_name": 1,
            "email": 1,
            "mobile_number": 1,
            "gender": 1,
            "is_enable": 1,
            "date_of_birth": 1,
            "login_type": 1,
            "user_status": 1,
            "role": 1,
            "user_type": 1,
            "is_blocked": 1,
            "email_verified": 1,
            "phone_verified": 1,
            "login_datetime": 1,
            "create_datetime": 1,
        }
        entities = await self.aggregate(
            pipeline=[
                {"$match": criteria},
                {"$project": {"_id": 0, **project}},
            ]
        )
        return entities, project.keys()


users_crud = UserCRUD(
    read_db_model=UserDBReadModel,
    create_db_model=UserDBCreateModel,
    update_db_model=UserDBUpdateModel,
)


class SavedBankCardCRUD(BaseCRUD):
    pass
