from src.core.base.crud import BaseCRUD
from .models import (
    StateDBCreateModel,
    StateDBReadModel,
    StateDBUpdateModel,
    CityDBCreateModel,
    CityDBReadModel,
    CityDBUpdateModel,
)


class StateCRUD(BaseCRUD):
    pass


state_crud = StateCRUD(
    create_db_model=StateDBCreateModel,
    read_db_model=StateDBReadModel,
    update_db_model=StateDBUpdateModel,
)


class CityCRUD(BaseCRUD):
    pass


city_crud = CityCRUD(
    create_db_model=CityDBCreateModel,
    read_db_model=CityDBReadModel,
    update_db_model=CityDBUpdateModel,
)
