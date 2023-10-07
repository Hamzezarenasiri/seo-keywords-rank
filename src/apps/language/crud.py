from src.apps.language.models import (
    LanguageDBCreateModel,
    LanguageDBReadModel,
    LanguageDBUpdateModel,
)
from src.core.base.crud import BaseCRUD


class LanguageCRUD(BaseCRUD):
    pass


languages_crud = LanguageCRUD(
    read_db_model=LanguageDBReadModel,
    create_db_model=LanguageDBCreateModel,
    update_db_model=LanguageDBUpdateModel,
)
