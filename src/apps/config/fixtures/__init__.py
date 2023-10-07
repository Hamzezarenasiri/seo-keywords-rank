from . import configs_fixture
from ..crud import configs_crud
from ..models import ConfigDBCreateModel


async def default_configs():
    if await configs_crud.count() == 0:
        await configs_crud.create(ConfigDBCreateModel(**configs_fixture.configs))


async def run_fixtures():
    await default_configs()
