from functools import lru_cache
from os import getenv

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv("../.env.local")
load_dotenv(".env.local")


class Settings(BaseModel):
    the_odds_api_key: str | None = None
    the_odds_api_base_url: str = "https://api.theoddsapi.com"
    odds_sport_key: str = "soccer_epl"
    odds_regions: str = "uk,eu"
    odds_markets: str = "h2h,totals"
    database_url: str = "sqlite:///./epl_odds_scanner.db"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        the_odds_api_key=getenv("THE_ODDS_API_KEY"),
        the_odds_api_base_url=getenv("THE_ODDS_API_BASE_URL", "https://api.theoddsapi.com"),
        odds_sport_key=getenv("ODDS_SPORT_KEY", "soccer_epl"),
        odds_regions=getenv("ODDS_REGIONS", "uk,eu"),
        odds_markets=getenv("ODDS_MARKETS", "h2h,totals"),
        database_url=getenv("DATABASE_URL", "sqlite:///./epl_odds_scanner.db"),
    )
