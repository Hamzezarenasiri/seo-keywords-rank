import importlib
import inspect
import pkgutil
import pyclbr
from typing import List


def get_models(app_settings, logger) -> list:
    """
    Scans `settings.apps_folder_name`.
    Find `models` modules in each of them and get all attributes there.
    :return: list of user-defined models (subclassed from BaseDBModel) in apps
    """
    from src.core.base.models import BaseDBReadModel

    apps_folder_name = app_settings.APPS_FOLDER_NAME
    models = []
    for app in app_settings.APPS:
        app_path = f"{apps_folder_name}/{app}"
        modules = [
            f for f in pkgutil.walk_packages(path=[app_path]) if f.name == "models"
        ]
        if not modules:
            continue
        for module in modules:
            path_to_models = f"{apps_folder_name}.{app}.models".replace("/", ".")
            mudule = importlib.import_module(path_to_models)
            if module.ispkg:
                module_models = [
                    x[0] for x in inspect.getmembers(mudule, inspect.isclass)
                ]
            else:
                try:
                    module_models = pyclbr.readmodule(path_to_models).keys()
                except (AttributeError, ImportError):
                    logger.warning(
                        f"Unable to read module attributes in {path_to_models}"
                    )
                    continue
            models.extend([getattr(mudule, model) for model in module_models])
    return list(filter(lambda x: issubclass(x, BaseDBReadModel), models))


async def create_indexes(app_settings, logger) -> List[str]:
    """
    Gets all models in project and then creates indexes for each one of them.
    :return: list of indexes that has been invoked to create
             (could've been created earlier, it doesn't raise in this case)
    """
    models = get_models(app_settings, logger)
    indexes = []
    for model in models:
        res = await model.create_indexes()
        indexes.append(res)
    return list(filter(None, indexes))


async def get_fixtures(app_settings, logger) -> list:
    apps_folder_name = app_settings.APPS_FOLDER_NAME
    funcs = []
    for app in app_settings.APPS:
        app_path = f"{apps_folder_name}/{app}"
        modules = [
            f for f in pkgutil.walk_packages(path=[app_path]) if f.name == "fixtures"
        ]
        if not modules:
            continue
        for module in modules:
            path_to_fixtures_func = f"{apps_folder_name}.{app}.fixtures".replace(
                "/", "."
            )
            mudule = importlib.import_module(path_to_fixtures_func)
            if module.ispkg:
                module_funcs = [
                    x[0] for x in inspect.getmembers(mudule, inspect.isfunction)
                ]
            else:
                try:
                    module_funcs = pyclbr.readmodule(path_to_fixtures_func).keys()
                except (AttributeError, ImportError):
                    logger.warning(
                        f"Unable to read module attributes in {path_to_fixtures_func}"
                    )
                    continue
            funcs.extend([getattr(mudule, func) for func in module_funcs])
    return list(filter(lambda x: x.__name__ == "run_fixtures", funcs))


async def create_fixtures(app_settings, logger):
    fixtures = await get_fixtures(app_settings, logger)
    for func in fixtures:
        await func()
