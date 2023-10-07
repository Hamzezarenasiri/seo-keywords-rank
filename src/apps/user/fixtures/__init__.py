from . import user_fixture
from ..crud import users_crud
from ..models import UserDBCreateModel


async def default_users():
    if await users_crud.count() == 0:
        for entity in user_fixture.all_users:
            await users_crud.create(UserDBCreateModel(**entity))


async def run_fixtures():
    await default_users()
