import abc


class BaseStorage(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    async def upload_object_binary(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    async def get_presigned_url(self, *args, **kwargs):
        pass
