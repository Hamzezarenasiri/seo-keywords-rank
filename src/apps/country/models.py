import pymongo
from typing import Optional, List
from pydantic import Field

from src.core.mixins.fields import PointField
from src.main.config import collections_names
from src.core import mixins
from src.core.mixins import DB_ID, default_id
from src.core.base.models import BaseDBModel, BaseDBReadModel


class StateBaseModel(
    BaseDBModel,
    mixins.IsEnableMixin,
    mixins.SoftDeleteMixin,
):
    name: str
    default_location: Optional[PointField]

    class Meta:
        collection_name = collections_names.STATES
        entity_name = "states"
        indexes = [
            pymongo.IndexModel("id", name="id", unique=True),
        ]


class StateDBReadModel(StateBaseModel, BaseDBReadModel):
    id: DB_ID


class StateDBCreateModel(StateBaseModel, mixins.CreateDatetimeMixin):
    id: DB_ID = Field(default_factory=default_id)


class StateDBUpdateModel(StateBaseModel, mixins.UpdateDatetimeMixin):
    name: Optional[str]


class CityBaseModel(
    BaseDBModel,
    mixins.IsEnableMixin,
    mixins.SoftDeleteMixin,
):
    name: str
    default_location: Optional[PointField]
    neighbourhoods: Optional[List[str]] = []
    buildings: Optional[List[str]] = []

    class Meta:
        collection_name = collections_names.CITIES
        entity_name = "cities"
        indexes = [
            pymongo.IndexModel("id", name="id", unique=True),
        ]


class CityDBReadModel(CityBaseModel, BaseDBReadModel):
    id: DB_ID
    state_id: DB_ID


class CityDBCreateModel(CityBaseModel, mixins.CreateDatetimeMixin):
    id: DB_ID = Field(default_factory=default_id)
    state_id: DB_ID


class CityDBUpdateModel(CityBaseModel, mixins.UpdateDatetimeMixin):
    name: Optional[str]
    neighbourhoods: Optional[List[str]]
    buildings: Optional[List[str]]
