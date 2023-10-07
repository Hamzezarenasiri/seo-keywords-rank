from enum import Enum
from typing import List


class ConfigNotFound404MessageEnum(str, Enum):
    config: str = "Config not found"
    no_docs: str = "Please insert config record into database."


class ConfigNotFound404DetailEnum(list, Enum):
    config: List[str] = ["Config not found"]
    no_docs: List[str] = ["configs collection is empty."]


class ConfigTypeAdmin(str, Enum):
    hashtags: str = "hashtags"
    number_of_humper: str = "number_of_humper"
    number_of_lollipop: str = "number_of_lollipop"
    crawl_interval: str = "crawl_interval"


ALL_ADMIN_CONFIG_TYPES = [i.value for i in ConfigTypeAdmin.__members__.values()]
