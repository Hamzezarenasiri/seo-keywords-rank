from enum import Enum


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
    add_keyword_rate: str = "add_keyword_rate"
    get_keyword_rates_average: str = "get_keyword_rates_average"


class KeywordErrorMessageEnum(str, Enum):
    not_found: str = "keyword_not_found"
    # not_found_or_disabled: str = "keyword_not_found_or_disabled"
    invalid_quantity: str = "invalid_quantity"
