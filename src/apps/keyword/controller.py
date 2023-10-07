from src.apps.keyword.crud import keywords_crud
from src.core.base.controller import BaseController


class KeywordController(BaseController):
    pass


keyword_controller = KeywordController(
    crud=keywords_crud,
)
