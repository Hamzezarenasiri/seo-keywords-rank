from src.core.common.exceptions import UpdateFailed
from src.services import global_services
from . import exception, schema as config_schema
from .crud import configs_crud
from .models import ConfigDBUpdateModel


class ConfigController(object):
    async def get_configs(
        self,
    ) -> config_schema.ConfigGetOut:
        result = await configs_crud.get_configs_object()
        if not result:
            raise exception.ConfigNotFound
        return result

    async def update_single_config(
        self,
        new_config_data: config_schema.ConfigUpdateIn,
    ) -> config_schema.ConfigUpdateOut:
        _, is_updated = await configs_crud.update_and_get(
            new_doc=ConfigDBUpdateModel(**new_config_data.dict()).dict(
                exclude_none=True
            ),
            criteria={},
        )

        if not is_updated:
            raise UpdateFailed
        global_services.ADMIN_SETTINGS = await configs_crud.get_configs_object()
        result = await self.get_configs()
        return config_schema.ConfigUpdateOut(**result.dict())


config_controller = ConfigController()
