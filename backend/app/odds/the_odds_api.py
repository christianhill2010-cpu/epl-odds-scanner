from app.config import get_settings
import httpx


class OddsApiConfigurationError(RuntimeError):
    pass


class OddsApiRequestError(RuntimeError):
    pass


class TheOddsApiClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return bool(self.settings.the_odds_api_key)

    def fetch_epl_odds(self) -> list[dict]:
        if not self.settings.the_odds_api_key:
            raise OddsApiConfigurationError("THE_ODDS_API_KEY is not configured")

        response = httpx.get(
            f"{self.settings.the_odds_api_base_url.rstrip('/')}/odds/",
            params={
                "sport_key": self.settings.odds_sport_key,
                "markets": self.settings.odds_markets,
                "regions": self.settings.odds_regions,
                "oddsFormat": "decimal",
            },
            headers={"x-api-key": self.settings.the_odds_api_key},
            timeout=20,
        )

        if response.status_code >= 400:
            raise OddsApiRequestError(
                f"The Odds API returned {response.status_code}: {response.text}"
            )

        payload = response.json()
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("data"), list):
            return payload["data"]

        raise OddsApiRequestError("The Odds API returned an unexpected response shape")
