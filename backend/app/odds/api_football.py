import httpx

from app.config import get_settings


class ApiFootballConfigurationError(RuntimeError):
    pass


class ApiFootballRequestError(RuntimeError):
    pass


class ApiFootballClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return bool(self.settings.api_football_key)

    def fetch_epl_odds(self) -> list[dict]:
        if not self.settings.api_football_key:
            raise ApiFootballConfigurationError("API_FOOTBALL_KEY is not configured")

        results: list[dict] = []
        page = 1
        total_pages = 1

        while page <= total_pages:
            payload = self._get_odds_page(page)
            results.extend(payload.get("response", []))

            paging = payload.get("paging", {})
            total_pages = int(paging.get("total") or 1)
            page += 1

        return results

    def _get_odds_page(self, page: int) -> dict:
        response = httpx.get(
            f"{self.settings.api_football_base_url.rstrip('/')}/odds",
            params={
                "league": self.settings.api_football_league_id,
                "season": self.settings.api_football_season,
                "page": page,
            },
            headers={"x-apisports-key": self.settings.api_football_key},
            timeout=20,
        )

        if response.status_code >= 400:
            raise ApiFootballRequestError(
                f"API-Football returned {response.status_code}: {response.text}"
            )

        payload = response.json()
        errors = payload.get("errors")
        if errors:
            raise ApiFootballRequestError(f"API-Football returned errors: {errors}")
        if not isinstance(payload.get("response"), list):
            raise ApiFootballRequestError("API-Football returned an unexpected response shape")

        return payload
