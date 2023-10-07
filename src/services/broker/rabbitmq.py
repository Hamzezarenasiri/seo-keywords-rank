import asyncio

import aio_pika
from aio_pika import Message
from aio_pika.pool import Pool


class AIOPikaClient(object):
    def __init__(
        self,
        url: str = None,
        host: str = None,
        port: int = None,
        login: str = None,
        password: str = None,
    ):
        self.url = url
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.loop = asyncio.get_event_loop()
        self.connection_pool = None
        self.channel_pool = None

    async def connect(self):
        self.connection_pool = Pool(self.get_connection, max_size=10, loop=self.loop)
        self.channel_pool = Pool(self.get_channel, max_size=10, loop=self.loop)

    def sync_connect(self):
        self.connection_pool = Pool(self.get_connection, max_size=10, loop=self.loop)
        self.channel_pool = Pool(self.get_channel, max_size=10, loop=self.loop)

    async def get_connection(self) -> aio_pika.Channel:
        return await aio_pika.connect_robust(
            url=self.url,
            host=self.host,
            port=self.port,
            login=self.login,
            password=self.password,
            loop=self.loop,
        )

    async def get_channel(self) -> aio_pika.Channel:
        async with self.connection_pool.acquire() as connection:
            return await connection.channel()

    async def publish(self, queue_name, body: bytes):
        async with self.channel_pool.acquire() as channel:  # type: aio_pika.Channel
            await channel.default_exchange.publish(
                Message(body),
                queue_name,
            )
