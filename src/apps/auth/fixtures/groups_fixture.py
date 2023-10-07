from src.apps.user.enum import DefaultGroupNameEnum
from .permissions_fixture import (
    admin_permissions,
    customer_permissions,
    super_admin_permissions,
    audit_permissions,
)

all_groups = {
    DefaultGroupNameEnum.super_admin: super_admin_permissions,
    DefaultGroupNameEnum.admin: admin_permissions,
    DefaultGroupNameEnum.customer: customer_permissions,
    DefaultGroupNameEnum.audit: audit_permissions,
}
