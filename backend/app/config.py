from functools import lru_cache
from os import getenv

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv("../.env.local")
load_dotenv(".env.local")


class Settings(BaseModel):
    the_odds_api_key: str | None = None
    database_url: str = "sqlite:///./epl_odds_scanner.db"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        the_odds_api_key=getenv("THE_ODDS_API_KEY"),
        database_url=getenv("DATABASE_URL", "sqlite:///./epl_odds_scanner.db"),
    )
