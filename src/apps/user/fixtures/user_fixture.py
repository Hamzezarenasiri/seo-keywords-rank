from src.core.security import user_password
from src.main.config import app_settings

all_users = [
    {
        "id": "971544814481",
        "is_blocked": False,
        "is_deleted": False,
        "is_enable": True,
        "is_force_change_password": False,
        "is_force_login": False,
        "mobile_number": "+989123456789",
        "email": "hamze@fanpino.com",
        "role": "admin",
        "hashed_password": str(
            user_password.get_password_hash(app_settings.DEFAULT_PASSWORD)
        ),
        "groups": ["admin"],
        "phone_verified": True,
        "email_verified": True,
        "user_status": "confirmed",
        "addresses": [],
        "gender": "male",
        "first_name": "Genesis",
        "last_name": "Admin",
        "permissions": [],
        "settings": {"language": "EN", "country_code": "UAE", "currency_code": "AED"},
    }
]
