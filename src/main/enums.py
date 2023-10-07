from enum import Enum


class CountryCode(str, Enum):
    emirates: str = "UAE"


ALL_COUNTRY_CODES = [i.value for i in CountryCode.__members__.values()]


class CurrencyCode(str, Enum):
    aed: str = "AED"
    # usd: str = "USD"


ALL_CURRENCY_CODES = [i.value for i in CurrencyCode.__members__.values()]
