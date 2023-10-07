import logging
from datetime import datetime

import devtools
import pymongo
from celery import Celery
from datetime import timezone

from celery.signals import after_setup_logger
from decouple import config as env_config
from celery.schedules import crontab

from src.main import config
from .web_scraper import get_rank

CELERY_BROKER_URL = env_config("CELERY_BROKER_URL")
CELERY_BACKEND_URL = env_config("CELERY_BACKEND_URL")

celery_worker = Celery("worker", broker=CELERY_BROKER_URL, backend=CELERY_BACKEND_URL)
celery_worker.config_from_object(config.celery_settings)


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # add filehandler
    fh = logging.FileHandler("celery.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


@celery_worker.task
def get_rank_task(keyword: str, domain: str, page: int = 1):
    rank = get_rank(keyword, domain, page=page)
    devtools.debug(rank)
    mongo = pymongo.MongoClient(config.db_settings.URI)
    keyword_db = mongo.get_database(config.db_settings.DATABASE_NAME)
    keyword_db.keywords.update_one(
        {"keyword": keyword, "domain": domain},
        {
            "$set": {
                "rank": rank,
                "last_rank_update_time": datetime.now(timezone.utc),
            }
        },
    )
    print(
        "-------------------------------- Finished get_rank_task --------------------------------"
    )
    mongo.disconnect()


@celery_worker.task
def get_rank_daily_task():
    print(
        "-------------------------------- start get_rank_daily_task --------------------------------"
    )
    mongo = pymongo.MongoClient(config.db_settings.URI)
    keyword_db = mongo.get_database(config.db_settings.DATABASE_NAME)
    keywords = keyword_db.keywords.find({"is_deleted": False}).sort(
        "last_rank_update_time"
    )
    for keyword in keywords:
        rank = get_rank(keyword.get("keyword"), keyword.get("domain"), page=1)
        devtools.debug(rank)
        keyword_db.keywords.update_one(
            {"keyword": keyword.get("keyword"), "domain": keyword.get("domain")},
            {
                "$set": {
                    "rank": rank,
                    "last_rank_update_time": datetime.now(timezone.utc),
                }
            },
        )
    print(
        "-------------------------------- Finished get_rank_daily_task --------------------------------"
    )
    mongo.disconnect()


celery_worker.conf.beat_schedule = {
    "get_rank_daily_task": {
        "task": "src.celery.get_rank_daily_task",
        "schedule": crontab(
            hour=22,
            minute=3,
        ),
    },
}
