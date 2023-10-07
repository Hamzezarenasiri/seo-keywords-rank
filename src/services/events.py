import logging

import celery

from src.core.aws.sns import SESHandler, SNSHandler
from src.core.logger import create_logger
from src.main import config
from .cache.base import BaseCache
from .cache.redis import Redis
from .db.base import BaseDB
from .db.mongodb import MongoDB
from .storage.aws_s3 import S3Handler


async def initialize_logger() -> logging.Logger:
    return create_logger(__name__, config.app_settings.LOG_LEVEL)


async def initialize_broker() -> celery.Celery:
    celery_app = celery.Celery("tasks")
    celery_app.config_from_object(config.celery_settings)
    return celery_app


async def initialize_cache() -> BaseCache:
    redis = Redis()
    await redis.connect(
        host=config.cache_settings.HOST,
        port=config.cache_settings.PORT,
        db=config.cache_settings.DB,
        password=config.cache_settings.PASSWORD,
        timeout=config.cache_settings.TIMEOUT_SECONDS,
    )
    return redis


async def initialize_db() -> BaseDB:
    mongo = MongoDB()
    await mongo.connect(
        uri=config.db_settings.URI,
        connection_timeout=config.db_settings.CONNECTION_TIMEOUT,
        min_pool_size=config.db_settings.MIN_POOL_SIZE,
        max_pool_size=config.db_settings.MAX_POOL_SIZE,
    )

    await mongo.get_database(database_name=config.db_settings.DATABASE_NAME)
    return mongo


async def initialize_storage() -> S3Handler:
    return S3Handler(
        access_key=config.aws_settings.ACCESS_KEY,
        secret_access=config.aws_settings.SECRET_ACCESS,
        region_name=config.aws_settings.REGION_NAME,
        bucket_name=config.aws_settings.S3_BUCKET_NAME,
        presigned_expiration=config.aws_settings.S3_PRESIGNED_EXPIRATION,
    )


async def initialize_ses() -> SESHandler:
    return SESHandler(
        access_key=config.aws_settings.ACCESS_KEY,
        secret_access=config.aws_settings.SECRET_ACCESS,
        region_name=config.aws_settings.SES_REGION_NAME,
        default_from_email=config.aws_settings.SES_DEFAULT_FROM_EMAIL,
    )


async def initialize_sns() -> SNSHandler:
    return SNSHandler(
        access_key=config.aws_settings.ACCESS_KEY,
        secret_access=config.aws_settings.SECRET_ACCESS,
        region_name=config.aws_settings.SES_REGION_NAME,
    )


async def close_db_connection(db: MongoDB) -> None:
    await db.disconnect()
