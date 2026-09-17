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

    response = client.post("/scans", json={"bankroll": 100})

    assert response.status_code == 400
    assert response.json()["detail"] == "THE_ODDS_API_KEY is not configured"
