from enum import Enum
from typing import List


class UserNotFoundErrorMessageEnum(str, Enum):
    not_found: str = "User not found"
    # not_found_or_disabled: str = "User not found or disabled"


class UserNotFoundErrorDetailEnum(List[str], Enum):
    not_found: List[str] = ["User not found"]


class UserForbiddenErrorMessageEnum(str, Enum):
    is_blocked: str = "your_account_is_blocked__please_contact_administrator"
    is_pending: str = "your_account_status_is_pending__please_contact_administrator"
    is_rejected: str = "your_account_status_is_rejected__please_contact_administrator"
    is_disabled: str = "your_account_is_disabled__please_contact_administrator"
    access_denied: str = "can_t_perform_this_action"
    phone_not_verified: str = "Phone not verified"
    email_not_verified: str = "Email not verified"


class UserForbiddenErrorDetailEnum(List[str], Enum):
    is_disabled: List[str] = ["The specified user is disabled"]
    is_blocked: List[str] = ["The specified user is blocked"]
    is_pending: List[str] = ["The specified user is pending"]
    is_rejected: List[str] = ["The specified user is rejected"]
    access_denied: List[str] = ["Can't perform this action"]
    phone_not_verified: List[str] = ["Phone not verified"]
    email_not_verified: List[str] = ["Email not verified"]


class UserMessageEnum(str, Enum):
    changed_password: str = "Success - Password changed successfully"
    get_customer_bank_cards: str = "get_customer_bank_cards"
    register_new_user_and_sent_otp: str = "register_new_user_and_sent_otp"


class UserDetailEnum(List[str], Enum):
    no_admin_for_user: List[str] = ["Failed"]


class UserBadRequestErrorMessageEnum(str, Enum):
    addresses: str = "Address IDs not found"
    google_code_not_valid: str = "google_code_not_valid"


class UserBadRequestErrorDetailEnum(List[str], Enum):
    addresses: List[str] = ["One or more Address IDs not found"]
    google_code_not_valid: List[str] = ["Google code not valid"]


class LoginType(str, Enum):
    direct: str = "direct"
    social: str = "social"


ALL_LOGIN_TYPES = [i.value for i in LoginType.__members__.values()]


class UserStatus(str, Enum):
    pending: str = "pending"
    just_joined: str = "just_joined"
    joined_club: str = "joined_club"
    confirmed: str = "confirmed"
    rejected: str = "rejected"


ALL_USER_STATUSES = [i.value for i in UserStatus.__members__.values()]


class UserType(str, Enum):
    parent: str = "parent"
    kid: str = "kid"


ALL_USER_TYPES = [i.value for i in UserType.__members__.values()]


class GenderEnum(str, Enum):
    female: str = "female"
    male: str = "male"
    other: str = "other"


ALL_GENDERS = [i.value for i in GenderEnum.__members__.values()]


class OfferEnum(str, Enum):
    offer: str = "offer"
    coupon: str = "coupon"
    other: str = "other"


ALL_OFFERS = [i.value for i in OfferEnum.__members__.values()]


class ShoppingDeviceEnum(str, Enum):
    mobile: str = "mobile"
    website: str = "website"
    other: str = "other"


ALL_SHOPPING_DEVICES = [i.value for i in ShoppingDeviceEnum.__members__.values()]


class BuyTimeEnum(str, Enum):
    sometimes: str = "sometimes"
    often: str = "often"
    rarely: str = "rarely"


ALL_BUY_TIMES = [i.value for i in BuyTimeEnum.__members__.values()]


class AddressType(str, Enum):
    pickup: str = "pickup"
    warehouse: str = "warehouse"
    work: str = "work"
    shipping_address: str = "shipping_address"
    billing_address: str = "billing_address"


ALL_Address_Types = [i.value for i in AddressType.__members__.values()]


class DefaultGroupNameEnum(str, Enum):
    super_admin: str = "super_admin"
    admin: str = "admin"
    customer: str = "customer"
    audit: str = "audit"


ALL_GROUP_NAMES = [i.value for i in DefaultGroupNameEnum.__members__.values()]


class DeviceType(str, Enum):
    iOS = "ios"
    android = "android"
    web = "web"
    other = "web"


class DeviceMessageEnum(str, Enum):
    add_new_device: str = "add_new_device"


class BusinessTypeEnum(str, Enum):
    PERSONAL: str = "personal"
    REAL_STATE: str = "real_state"
    SHOP: str = "shop"


class UserBlockReasonEnum(str, Enum):
    SEXUAL_HARASSMENT = "sexual harassment"
    PRIVACY_VIOLATION = "privacy violation"
    WORD_ABUSE = "word abuse"
    INSULT = "insult"
    FRAUD = "fraud"
    DISTURBANCE = "disturbance"
    FAKE_NAME = "fake name"
    BOT = "bot"
    OTHER = "other"
