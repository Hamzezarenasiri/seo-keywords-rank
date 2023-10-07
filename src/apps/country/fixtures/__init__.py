from src.apps.country.models import CityDBCreateModel, StateDBCreateModel
from src.apps.country.crud import city_crud, state_crud
from .country_fixtures import all_cities, all_states


async def default_cities():
    if await city_crud.count() == 0:
        for city in all_cities:
            await city_crud.create(CityDBCreateModel(**city))


async def default_states():
    if await state_crud.count() == 0:
        for state in all_states:
            await state_crud.create(StateDBCreateModel(**state))


async def run_fixtures():
    await default_cities()
    await default_states()
