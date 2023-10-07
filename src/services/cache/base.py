import abc
from typing import Any, Optional


class BaseCache(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def set(self, key: str, value: Any, expiry: Optional[int] = None):
        ...

    @abc.abstractmethod
    async def get(self, key: str) -> bytes:
        ...

    @abc.abstractmethod
    async def delete(self, key: str):
        ...
