from enum import Enum
from typing import List


class ServerError500MessageEnum(str, Enum):
    server_error: str = "Internal server error, try again later"


class ServerError500DetailEnum(List[str], Enum):
    server_error: List[str] = ["Internal server error, try again later"]


class BadRequest400MessageEnum(str, Enum):
    delete_failed: str = "Delete failed"
    update_failed: str = "Update failed"


class BadRequest400DetailEnum(List[str], Enum):
    delete_failed: List[str] = ["Delete failed"]
    update_failed: List[str] = ["Update failed"]


class Unauthorized401MessageEnum(str, Enum):
    limited_token: str = "Limited token"
    invalid_token: str = "Your session has expired, please login again!"
    invalid_temp_token: str = "Invalid temp token. please login again "
    access_token_expired: str = "Access token expired"
    refresh_token_expired: str = "Refresh token expired"


class Unauthorized401DetailEnum(List[str], Enum):
    limited_token: List[str] = ["Limited token"]
    invalid_token: List[str] = ["Invalid token provided"]
    invalid_temp_token: List[str] = ["Invalid temp token. please login again "]
    access_token_expired: List[str] = ["Access token expired"]
    refresh_token_expired: List[str] = ["Refresh token expired"]


class Forbidden403MessageEnum(str, Enum):
    detail: str = "Forbidden action."
    user_not_allowed: str = "User is not allowed to perform this action."
    access_denied: str = "Access denied"


class Forbidden403DetailEnum(List[str], Enum):
    detail: List[str] = ["Forbidden action."]
    user_not_allowed: List[str] = ["User is not allowed to perform this action."]
    access_denied: List[str] = ["Access denied"]


class NotFound404MessageEnum(str, Enum):
    detail: str = "Not found."
    user: str = "User not found."


class Conflict409MessageEnum(str, Enum):
    detail: str = "Duplicated entry."


class FileSizeTooLarge413MessageEnum(str, Enum):
    file: str = "File size is too large"


class UpdatePass422MessageEnum(str, Enum):
    old_password_not_match: str = "Old password not match"


class UpdatePass422DetailEnum(List[str], Enum):
    old_password_not_match: List[str] = ["Old password not match"]


class QueryParams422MessageEnum(str, Enum):
    invalid_query_params: str = "Invalid query params"


class QueryParams422DetailEnum(List[str], Enum):
    invalid_query_params: List[str] = ["Invalid query params"]
