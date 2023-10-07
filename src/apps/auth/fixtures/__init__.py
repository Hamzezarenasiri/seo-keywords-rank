from . import entities_fixture, groups_fixture
from ..crud import entities_crud, groups_crud
from ..models import EntityDBCreateModel, GroupDBCreateModel


async def default_entities():
    if await entities_crud.count() == 0:
        for entity in entities_fixture.all_entities_default:
            await entities_crud.create(EntityDBCreateModel(**entity))


async def default_groups():
    if await groups_crud.count() == 0:
        for name, permissions in groups_fixture.all_groups.items():
            await groups_crud.create(
                GroupDBCreateModel(name=name, permissions=list(permissions))
            )


async def run_fixtures():
    await default_entities()
    await default_groups()
