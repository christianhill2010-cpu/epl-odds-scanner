from functools import lru_cache
from os import getenv

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv("../.env.local")
load_dotenv(".env.local")


class Settings(BaseModel):
    odds_provider: str = "api_football"
    the_odds_api_key: str | None = None
    the_odds_api_base_url: str = "https://api.theoddsapi.com"
    odds_sport_key: str = "soccer_epl"
    odds_regions: str = "uk,eu"
    odds_markets: str = "h2h,totals"
    api_football_key: str | None = None
    api_football_base_url: str = "https://v3.football.api-sports.io"
    api_football_league_id: int = 39
    api_football_season: int = 2026
    database_url: str = "sqlite:///./epl_odds_scanner.db"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        odds_provider=getenv("ODDS_PROVIDER", "api_football"),
        the_odds_api_key=getenv("THE_ODDS_API_KEY"),
        the_odds_api_base_url=getenv("THE_ODDS_API_BASE_URL", "https://api.theoddsapi.com"),
        odds_sport_key=getenv("ODDS_SPORT_KEY", "soccer_epl"),
        odds_regions=getenv("ODDS_REGIONS", "uk,eu"),
        odds_markets=getenv("ODDS_MARKETS", "h2h,totals"),
        api_football_key=getenv("API_FOOTBALL_KEY"),
        api_football_base_url=getenv(
            "API_FOOTBALL_BASE_URL",
            "https://v3.football.api-sports.io",
        ),
        api_football_league_id=int(getenv("API_FOOTBALL_LEAGUE_ID", "39")),
        api_football_season=int(getenv("API_FOOTBALL_SEASON", "2026")),
        database_url=getenv("DATABASE_URL", "sqlite:///./epl_odds_scanner.db"),
    )
