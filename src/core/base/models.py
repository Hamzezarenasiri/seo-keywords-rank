import abc
from datetime import datetime
from typing import Optional, List

from src.core.mixins.models import AddFieldsBaseModel
from src.services import global_services


class BaseDBModel(metaclass=abc.ABCMeta):
    class Config:
        anystr_strip_whitespace = True

    class Meta:
        pass

    @classmethod
    async def create_indexes(cls) -> Optional[List[str]]:
        if hasattr(cls.Meta, "indexes"):
            return await global_services.DB.create_indexes(cls)


class BaseDBReadModel(AddFieldsBaseModel):
    create_datetime: datetime
    update_datetime: Optional[datetime]
