from src.core.base.schema import BaseSchema


class BaseKeywordSchema(BaseSchema):
    keyword: str
    domain: str
    rank: None | int


class KeywordCreateIn(BaseKeywordSchema):
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


class KeywordUpdateIn(BaseKeywordSchema):
    pass


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
