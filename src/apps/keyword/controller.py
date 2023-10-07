from datetime import datetime, timezone

import devtools
import pymongo

from src.apps.keyword.crud import keywords_crud
from src.core.base.controller import BaseController
from src.main import config
from src.web_scraper import get_rank


class KeywordController(BaseController):
    def get_and_update_rank(self, keyword: str, domain: str):
        rank = get_rank(keyword, domain, page=1)
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

    def update_all_rank(self):
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


keyword_controller = KeywordController(
    crud=keywords_crud,
)
