from app.config import get_settings


class TheOddsApiClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return bool(self.settings.the_odds_api_key)
