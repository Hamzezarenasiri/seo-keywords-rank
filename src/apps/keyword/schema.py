from datetime import datetime

from src.core.base.schema import BaseSchema


class BaseKeywordSchema(BaseSchema):
    keyword: str
    domain: str
    rank: None | int
    create_datetime: None | datetime
    last_rank_update_time: None | datetime


class KeywordCreateIn(BaseSchema):
    keyword: str
    domain: str


class KeywordCreateOut(BaseKeywordSchema):
    rank: None | int


class KeywordGetOut(KeywordCreateOut):
    pass


class AdminKeywordsGetKeywordSubListOut(BaseKeywordSchema):
    pass


class KeywordsGetSubListOut(BaseKeywordSchema):
    pass


class KeywordUpdateIn(BaseSchema):
    keyword: None | str
    domain: None | str


class KeywordUpdateOut(BaseKeywordSchema):
    ...


class KeywordBulkUpdateOut(BaseKeywordSchema):
    pass


class KeywordBulkUpdateIn(BaseKeywordSchema):
    pass


class KeywordDetailSchema(BaseKeywordSchema):
    pass


class KeywordListSchema(BaseKeywordSchema):
    pass
