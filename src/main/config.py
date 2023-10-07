from decimal import Decimal
from typing import Dict, List, Optional, Union

from pydantic import (
    AnyHttpUrl,
    BaseSettings as PydanticBaseSettings,
    validator,
    Field,
    EmailStr,
)

from src.apps.config.common_model import OfficeAddress
from src.apps.language.enum import LanguageEnum
from src.main.enums import CountryCode, CurrencyCode

__all__ = (
    "admin_settings",
    "api_settings",
    "app_settings",
    "aws_settings",
    "cache_settings",
    "collections_names",
    "db_settings",
    "jwt_settings",
    "region_settings",
    "test_settings",
)


class BaseSettings(PydanticBaseSettings):
    class Config(PydanticBaseSettings.Config):
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class AppSettings(BaseSettings):
    OTP_LENGTH: int = 5
    OTP_TIME: int = 2 * 60
    PROJECT_NAME: str = "keywords ProjectWebsite"
    PROJECT_DESCRIPTION: str = "keywords ProjectWebsite"
    LOG_LEVEL: str = "INFO"
    PROJECT_SERVERS: List[Dict[str, str]] = [{"url": "http://localhost:8080"}]
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    DEBUG: bool = False
    SENDER_EMAIL: str = "support@calitsu.com"
    REPLY_RECEIVER_EMAIL: str = "support@calitsu.com"
    OTP_TEMPLATE: str = "keywords Project verification code: {otp}"
    OTP_SUBJECT: str = "keywords ProjectOne-Time Password"
    COUPON_CODE_TEMPLATE: str = "Your keywords ProjectCoupon: {coupon_code}"

    USER_AVATAR_MAX_FILE_SIZE: int = 2**20
    DEFAULT_MAX_STR_LENGTH: int = 3145728  # 3MB
    USER_AVATAR_SUPPORTED_FORMATS: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/svg+xml",
    ]
    APP_RELOAD: Optional[bool] = False
    REQUEST_ATTACHMENT_MAX_FILE_SIZE: int = 2**30 * 2
    REQUEST_ATTACHMENT_SUPPORTED_FORMATS: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/svg+xml",
        "video/x-flv",
        "video/mp4",
        "application/x-mpegURL",
        "video/MP2T",
        "video/3gpp",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-ms-wmv",
    ]

    CRYPTO_KEY: str = "Behtarin_S3cr3t_k3y"
    TEST_MODE: bool = False
    SENTRY_DSN: Optional[str] = None
    DEFAULT_CURRENCY_CODE: CurrencyCode = CurrencyCode.aed
    DEFAULT_LANGUAGE: LanguageEnum = LanguageEnum.english
    DEFAULT_COUNTRY_CODE: CountryCode = CountryCode.emirates

    DEFAULT_MEDIA_PATH: str = "media"
    DEFAULT_FILES_PATH: str = f"{DEFAULT_MEDIA_PATH}/files"
    DEFAULT_AVATARS_PATH: str = f"{DEFAULT_MEDIA_PATH}/users/avatars"
    MEDIA_SERVER: str = "https://keywords-api.fanpino.com"
    DEFAULT_PASSWORD: str = "0123456789"
    APPS_FOLDER_NAME: str = "app/apps"
    APPS: List[str] = [
        "auth",
        "config",
        "file",
        "user",
        "advertisement",
        "promotion",
        "favourite",
        "view",
        "offer",
        "country",
        "category",
        "report",
        "static_info",
        "contact_us",
        "banner",
        "log_app",
        "chat",
    ]


app_settings = AppSettings()


class FilePaths(BaseSettings):
    DEFAULT_MEDIA_PATH: str = "app/media"

    class Config(BaseSettings.Config):
        env_prefix = "FILES_"


file_paths = FilePaths()


class CollectionsNames(BaseSettings):
    CONFIGS: str = "configs"
    ENTITIES: str = "entities"
    FILES: str = "files"
    GROUPS: str = "groups"
    LANGUAGES: str = "languages"
    LOGS: str = "logs"
    RULES: str = "rules"
    USERS: str = "users"
    STATES: str = "states"
    CITIES: str = "cities"
    KEYWORDS: str = "keywords"


collections_names = CollectionsNames()


class RegionSettings(BaseSettings):
    DEFAULT: str = "AE"

    class Config(BaseSettings.Config):
        env_prefix = "REGION_"


region_settings = RegionSettings()


class DBSettings(BaseSettings):
    URI: str
    DATABASE_NAME: str = "keywords"
    MIN_POOL_SIZE: int = 10
    MAX_POOL_SIZE: int = 50
    CONNECTION_TIMEOUT: int = 10000

    class Config(BaseSettings.Config):
        env_prefix = "DB_"


db_settings = DBSettings()


class ApiSettings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    BACKEND_CORS_METHODS: List[str] = ["*"]
    BACKEND_CORS_HEADERS: List[str] = ["*"]

    # pylint: disable=no-self-argument,no-self-use
    @validator("BACKEND_CORS_ORIGINS", pre=True, allow_reuse=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config(BaseSettings.Config):
        env_prefix = "API_"


api_settings = ApiSettings()


class CacheSettings(BaseSettings):
    HOST: str
    PORT: int = 6379
    DB: int = 2
    PASSWORD: Optional[str]
    TIMEOUT_SECONDS: Optional[int] = 5

    class Config(BaseSettings.Config):
        env_prefix = "CACHE_"


cache_settings = CacheSettings()


class CelerySettings(BaseSettings):
    # BROKER_URL: str = "redis://"
    # BROKER_URL: str = f"redis://{cache_settings.HOST}:{cache_settings.PORT}"
    # RESULT_BACKEND: str = "rpc://"
    timezone: str = "Asia/Tehran"
    # broker_transport: str = "redis"
    # broker_transport_options = {
    #     "max_retries": 3,
    #     "interval_start": 0,
    #     "interval_step": 0.2,
    #     "interval_max": 0.2,
    # }
    broker_connection_max_retries: int = 5
    broker_connection_timeout: int = 5
    broker_pool_limit: int = 3
    worker_concurrency: int = 4
    task_track_started: bool = True
    broker_connection_retry_on_startup: bool = True

    class Config(BaseSettings.Config):
        env_prefix = "CELERY_"


celery_settings = CelerySettings()


class JWTSettings(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_LIFETIME_SECONDS: int = 3600
    REFRESH_TOKEN_LIFETIME_SECONDS: int = 36000
    ALGORITHM: str = "HS256"

    class Config(BaseSettings.Config):
        env_prefix = "JWT_"


jwt_settings = JWTSettings()


class AWSSettings(BaseSettings):
    ACCESS_KEY: str
    SECRET_ACCESS: str
    REGION_NAME: str
    SES_REGION_NAME: Optional[str] = "me-south-1"
    SNS_REGION_NAME: Optional[str] = "me-south-1"
    SES_DEFAULT_FROM_EMAIL: Optional[str] = "info@fanpino.com"
    S3_BUCKET_NAME: str
    S3_PRESIGNED_EXPIRATION: int = 3600

    class Config(BaseSettings.Config):
        env_prefix = "AWS_"


aws_settings = AWSSettings()


class TestSettings(BaseSettings):
    DEFAULT_PASS: str = "pass_test"
    DEFAULT_PASS2: str = "1234 qwer"
    DEFAULT_OTP: str = "12345"
    DEFAULT_OTP_TIME: int = 50
    DEFAULT_EMAIL: str = "akhaxari@gmail.com"
    DEFAULT_PHONE: str = "+989127634520"

    class Config(BaseSettings.Config):
        env_prefix = "TEST_"


test_settings = TestSettings()


class FacebookSettings(BaseSettings):
    CLIENT_ID: str = "1164730914023254"
    CLIENT_SECRET: str = "1e9efacccac79de6c8a2b7e291c1d05a"
    REDIRECT_URI: AnyHttpUrl = str(
        app_settings.PROJECT_SERVERS[0]["url"]
        + api_settings.API_V1_STR
        + "/auth/login/fb"
    ).replace("http://", "https://")

    class Config(BaseSettings.Config):
        env_prefix = "FACEBOOK_"


facebook_settings = FacebookSettings()


class GoogleSettings(BaseSettings):
    CLIENT_ID: str
    CLIENT_SECRET: str
    LOGIN_REDIRECT_URI: AnyHttpUrl = str(
        app_settings.PROJECT_SERVERS[0]["url"]
        + api_settings.API_V1_STR
        + "/auth/login/google"
    ).replace("http://", "https://")
    APPLICATION_CREDENTIALS: str = "GoogleApplicationCredentialsKey.json"

    class Config(BaseSettings.Config):
        env_prefix = "GOOGLE_"


google_settings = GoogleSettings()


class AdminSettings(BaseSettings):
    auto_confirmation: Optional[bool] = True
    default_min_stock_quantity: Optional[int] = 1
    express_shipping_cost: Decimal = Decimal()
    is_enable: Optional[bool] = True
    is_deleted: Optional[bool] = True
    office_address: Optional[OfficeAddress] = OfficeAddress()
    shipping_guarantee: Decimal = Decimal()
    shipping_max_time_minutes: Optional[int] = 2000
    shipping_min_time_minutes: Optional[int] = 120
    offer_icon: Optional[str]
    other_configs: Optional[dict] = {}
    vat_rate: Optional[float] = Field(0, gte=0, lte=1)
    default_email_recipients: Optional[List[EmailStr]] = []

    class Config(BaseSettings.Config):
        env_prefix = "ADMIN_"
        arbitrary_types_allowed = True


admin_settings = AdminSettings()
