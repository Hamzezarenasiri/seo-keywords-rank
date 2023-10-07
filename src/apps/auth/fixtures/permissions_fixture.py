from src.apps.auth.fixtures.entities_fixture import all_entities

all_permissions_default = [
    {"entity": entity["code_name"], "rules": entity["rules"]} for entity in all_entities
]

super_admin_permissions = [
    {
        "entity": "configs",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "categories",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "files",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "gateways",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "groups",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "languages",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {"entity": "logs", "rules": ["list", "create", "read", "update", "delete", "menu"]},
    {
        "entity": "rules",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "users",
        "rules": [
            "list",
            "create",
            "read",
            "update",
            "delete",
            "menu",
            "activation",
            "blocking",
            "change_password",
        ],
    },
    {
        "entity": "countries",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "dashboards",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "products",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "tags",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "flavors",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "notifications",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "blogs",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "news",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "order_packs",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "shipping_packages",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "sliders",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "promotions",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "discounts",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "email_subscriptions",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "advertisements",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "promotions",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "cities",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "states",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "offers",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "ad_reports",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "user_reports",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "contact_us",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "static_infos",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
]

admin_permissions = [
    {
        "entity": "configs",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "categories",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "files",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "gateways",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "groups",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "languages",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {"entity": "logs", "rules": ["list", "create", "read", "update", "delete", "menu"]},
    {"entity": "rules", "rules": ["list", "read", "menu"]},
    {
        "entity": "users",
        "rules": [
            "list",
            "create",
            "read",
            "update",
            "delete",
            "menu",
            "activation",
            "blocking",
            "change_password",
        ],
    },
    {
        "entity": "countries",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "dashboard",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "products",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "banners",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "club_users",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "testimonials",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "coupons",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "orders",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "tags",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "flavors",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "notifications",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "blogs",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "news",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "order_packs",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "shipping_packages",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "sliders",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "promotions",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "discounts",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "email_subscriptions",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "advertisements",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "promotions",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "cities",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "states",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "offers",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "ad_reports",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "user_reports",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "static_infos",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "contact_us",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
]

customer_permissions = [
    {
        "entity": "files",
        "rules": ["list", "read", "menu"],
    },
    {
        "entity": "categories",
        "rules": ["list", "read"],
    },
    {
        "entity": "products",
        "rules": ["list", "read", "menu"],
    },
    {
        "entity": "tags",
        "rules": ["list", "read"],
    },
    {
        "entity": "flavors",
        "rules": ["list", "read"],
    },
    {
        "entity": "advertisements",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "promotions",
        "rules": ["list"],
    },
    {
        "entity": "favourites",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "views",
        "rules": ["create"],
    },
    {
        "entity": "offers",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "cities",
        "rules": ["list"],
    },
    {
        "entity": "states",
        "rules": ["list"],
    },
    {
        "entity": "ad_reports",
        "rules": ["create"],
    },
    {
        "entity": "static_infos",
        "rules": ["list", "read"],
    },
    {
        "entity": "contact_us",
        "rules": ["create"],
    },
    {
        "entity": "banners",
        "rules": ["list", "read"],
    },
]

audit_permissions = [
    {
        "entity": "files",
        "rules": ["list", "read", "menu"],
    },
    {
        "entity": "categories",
        "rules": ["list", "read"],
    },
    {
        "entity": "flavors",
        "rules": ["list", "read"],
    },
    {
        "entity": "advertisements",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "ad_reports",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {
        "entity": "user_reports",
        "rules": ["list", "create", "read", "update", "delete", "menu"],
    },
    {"entity": "logs", "rules": ["list", "create"]},
    {"entity": "users", "rules": ["list", "read", "update"]},
]
