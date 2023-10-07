from enum import Enum
from typing import List


class AuthOTPTypeEnum(str, Enum):
    sms: str = "sms"
    email: str = "email"


class AuthMessageEnum(str, Enum):
    login_username_password: str = "login_username_password"
    register_customer: str = "register_customer"
    otp_request: str = "otp_request"
    logout_user: str = "logout_user"
    google_login: str = "google_login"
    facebook_login: str = "facebook_login"
    refresh_token: str = "refresh_token"
    changed_password: str = "changed_password"
    changed_password_failed: str = "changed_password_failed"
    otp_verify_limited: str = "otp_verify_limited"


class AuthErrorMessageEnum(str, Enum):
    changed_password: str = "Failed - Password changed unsuccessful"
    user_exists_email: str = "user already exists with this email"
    user_exists_phone: str = "user already exists with this phone"
    social_login_failed: str = "Social Login Failed"


class AuthForbidden403MessageEnum(str, Enum):
    time: str = "current_date_is_not_between_user_start_date_and_end_date"
    block: str = "the_specified_user_is_blocked"
    permission_denied: str = "permission_denied"
    is_force_login: str = "you_must_login_again"


class AuthForbidden403DetailEnum(list, Enum):
    time: List[str] = ["Current date is not between user start date & end date"]
    block: List[str] = ["The Specified User Is Blocked"]
    permission_denied: List[str] = ["Permission denied."]
    is_force_login: List[str] = ["You must login again "]


class AuthNotFound404MessageEnum(str, Enum):
    user: str = "user_not_found"
    otp_expired: str = "otp_expired_or_invalid"


class AuthNotFound404DetailEnum(List[str], Enum):
    user: List[str] = ["User not found"]
    otp_expired: List[str] = ["OTP expired or invalid"]


class AuthConflict409MessageEnum(str, Enum):
    invalid_password: str = "Invalid password"


class GroupMessageEnum(str, Enum):
    create_new_group: str = "create_new_group"
    get_groups: str = "get_groups"
    get_single_group: str = "get_single_group"
    update_group: str = "update_group"


class GroupErrorMessageEnum(str, Enum):
    groups_have_user: str = "groups_have_user"


class OTPExistsErrorMessageEnum(str, Enum):
    otp_exists: str = (
        "we have already sent you verification code please try again later"
    )


class OTPExpiredErrorMessageEnum(str, Enum):
    otp_expired: str = "otp expired or invalid"
