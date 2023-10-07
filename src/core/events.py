from typing import Callable

from src import services
from src.apps.config.crud import configs_crud
from src.core.base.db_utils import create_indexes, create_fixtures
from src.main.config import app_settings
from src.services import global_services
from src.services import events


def create_start_app_handler() -> Callable:
    async def start_app() -> None:
        services.global_services.LOGGER = await events.initialize_logger()
        services.global_services.LOGGER.info("LOGGER Connected :)")
        services.global_services.DB = await events.initialize_db()
        services.global_services.LOGGER.info("DB Connected :)")
        await create_indexes(
            app_settings=app_settings, logger=services.global_services.LOGGER
        )
        services.global_services.LOGGER.info("Create DB indexes")
        await create_fixtures(
            app_settings=app_settings, logger=services.global_services.LOGGER
        )
        services.global_services.LOGGER.info("DB Fixtures Created")
        services.global_services.S3 = await events.initialize_storage()
        services.global_services.LOGGER.info("S3 Connected :)")
        services.global_services.SES = await events.initialize_ses()
        services.global_services.LOGGER.info("SES Connected :)")
        services.global_services.SNS = await events.initialize_sns()
        services.global_services.LOGGER.info("SNS Connected :)")
        services.global_services.CACHE = await events.initialize_cache()
        services.global_services.LOGGER.info("CACHE Connected :)")
        services.global_services.BROKER = await events.initialize_broker()
        services.global_services.ADMIN_SETTINGS = (
            await configs_crud.get_configs_object()
        )
        services.global_services.LOGGER.info("Set Admin Configs")
        services.global_services.LOGGER.info("running ... :)")

    return start_app


def create_stop_app_handler() -> Callable:
    async def stop_app() -> None:
        print("shutting down...")
        await events.close_db_connection(global_services.DB)
        services.global_services.LOGGER.info("entries deleted")

    return stop_app
