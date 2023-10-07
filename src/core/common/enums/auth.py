from enum import Enum


class RoleEnum(str, Enum):
    admin: str = "admin"
    customer: str = "customer"
    audit: str = "audit"


ALL_ROLES = [i.value for i in RoleEnum.__members__.values()]
