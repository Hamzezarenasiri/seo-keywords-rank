from typing import TypeVar, Optional, Type

from src.core.aws.sns import SESHandler, SNSHandler
from src.main.config import AdminSettings
from .cache.base import BaseCache

T = TypeVar("T")


class Services(object):
    ADMIN_SETTINGS: Optional[AdminSettings] = None
    BROKER: T = None
    CACHE: Optional[Type[BaseCache]] = None
    DB: T = None
    GOOGLE: T = None
    LOGGER: T = None
    S3: T = None
    SES: Optional[SESHandler] = None
    SNS: Optional[SNSHandler] = None


global_services = Services()
