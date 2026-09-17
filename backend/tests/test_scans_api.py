from fastapi.testclient import TestClient

from app.api import scans
from app.main import app
from app.odds.the_odds_api import OddsApiConfigurationError


def test_run_scan_demo_mode_returns_demo_opportunity() -> None:
    client = TestClient(app)

    response = client.post("/scans", json={"bankroll": 100, "demo": True})

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "demo"
    assert payload["evaluated_market_count"] == 1
    assert payload["opportunity_count"] == 1


def test_run_scan_live_mode_requires_api_key(monkeypatch) -> None:
    class FakeClient:
        def fetch_epl_odds(self) -> list[dict]:
            raise OddsApiConfigurationError("THE_ODDS_API_KEY is not configured")

    monkeypatch.setattr(scans, "TheOddsApiClient", FakeClient)
    client = TestClient(app)

    response = client.post(
        "/scans",
        json={"bankroll": 100, "source": "the_odds_api"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "THE_ODDS_API_KEY is not configured"


def test_run_scan_api_football_source(monkeypatch) -> None:
    class FakeApiFootballClient:
        def fetch_epl_odds(self) -> list[dict]:
            return [
                {
                    "fixture": {"id": 123},
                    "teams": {
                        "home": {"name": "Arsenal"},
                        "away": {"name": "Chelsea"},
                    },
                    "bookmakers": [
                        {
                            "name": "Bet365",
                            "bets": [
                                {
                                    "name": "Match Winner",
                                    "values": [
                                        {"value": "Home", "odd": "2.20"},
                                        {"value": "Draw", "odd": "3.80"},
                                        {"value": "Away", "odd": "4.00"},
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ]

    monkeypatch.setattr(scans, "ApiFootballClient", FakeApiFootballClient)
    client = TestClient(app)

    response = client.post("/scans", json={"bankroll": 100, "source": "api_football"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "api_football"
    assert payload["evaluated_market_count"] == 1
    assert payload["opportunity_count"] == 1
