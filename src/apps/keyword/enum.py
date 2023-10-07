from enum import Enum
from typing import List


class KeywordNotFoundErrorMessageEnum(str, Enum):
    not_found: str = "Keyword not found"
    # not_found_or_disabled: str = "Keyword not found or disabled"


class KeywordNotFoundErrorDetailEnum(List[str], Enum):
    not_found: List[str] = ["Keyword not found"]


class KeywordForbiddenErrorMessageEnum(str, Enum):
    is_blocked: str = "Your account is blocked, please contact administrator"
    is_disabled: str = "Your account is disabled, please contact administrator"
    access_denied: str = "Can't perform this action"


class KeywordForbiddenErrorDetailEnum(List[str], Enum):
    is_disabled: List[str] = ["The specified keyword is disabled"]
    is_blocked: List[str] = ["The specified keyword is blocked"]
    access_denied: List[str] = ["Can't perform this action"]


class KeywordMessageEnum(str, Enum):
    create_new_keyword: str = "create_new_keyword"
    get_keywords: str = "get_keywords"
    get_single_keyword: str = "get_single_keyword:"
    update_single_keyword: str = "update_single_keyword"
    bulk_update_keywords: str = "bulk_update_keywords"
    change_keywords_status: str = "change_keywords_status"
    get_keyword_rates: str = "get_keyword_rates"
    get_keyword_reviews: str = "get_keyword_reviews"
    change_reviews_status: str = "change_reviews_status"
    create_new_review: str = "create_new_review"
    get_keywords_statistics: str = "get_keywords_statistics"
    get_CSV_import_history: str = "get_CSV_import_history"
    get_single_CSV_import: str = "get_single_CSV_import"
    export_keyword_CSV: str = "export_keyword_CSV"
    keywords_upload_CSV: str = "keywords_upload_CSV"
    add_keyword_to_favourites: str = "add_keyword_to_favourites"
    delete_keyword_from_favourites: str = "delete_keyword_from_favourites"
    add_keyword_rate: str = "add_keyword_rate"
    get_keyword_rates_average: str = "get_keyword_rates_average"


class KeywordErrorMessageEnum(str, Enum):
    not_found: str = "keyword_not_found"
    # not_found_or_disabled: str = "keyword_not_found_or_disabled"
    invalid_quantity: str = "invalid_quantity"


class KeywordDetailEnum(List[str], Enum):
    no_admin_for_keyword: List[str] = ["Failed"]


class KeywordBadRequestErrorMessageEnum(List[str], Enum):
    addresses: List[str] = ["Address IDs not found"]


class KeywordBadRequestErrorDetailEnum(List[str], Enum):
    addresses: List[str] = ["One or more Address IDs not found"]


class KeywordType(str, Enum):
    type1: str = "type1"
    type2: str = "type2"


ALL_KEYWORD_TYPES = [i.value for i in KeywordType.__members__.values()]


class KeywordStatus(str, Enum):
    draft: str = "draft"
    published: str = "published"
    rejected: str = "rejected"


ALL_KEYWORD_STATUSES = [i.value for i in KeywordStatus.__members__.values()]


class KeywordErrorDetailEnum(list, Enum):
    not_found: List[str] = ["Keyword not found"]
    invalid_quantity: List[str] = ["invalid quantity"]
    duplicated_detail: List[str] = ["duplicated detail"]
    duplicated_detail_id: List[str] = ["duplicated detail id"]
