from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.arbitrage.calculator import OutcomePrice, evaluate_market
from app.config import get_settings
from app.normalization.markets import normalize_odds_events
from app.odds.api_football import (
    ApiFootballClient,
    ApiFootballConfigurationError,
    ApiFootballRequestError,
)
from app.odds.the_odds_api import (
    OddsApiConfigurationError,
    OddsApiRequestError,
    TheOddsApiClient,
)

router = APIRouter(prefix="/scans", tags=["scans"])


class ScanRequest(BaseModel):
    bankroll: float = Field(default=100.0, gt=0)
    demo: bool = False
    source: str | None = None


class ScanResponse(BaseModel):
    mode: str
    scanned_at: datetime
    evaluated_market_count: int
    opportunity_count: int
    opportunities: list[dict]
    warnings: list[str]


@router.post("", response_model=ScanResponse)
def run_scan(request: ScanRequest) -> ScanResponse:
    if request.demo:
        return _run_demo_scan(request.bankroll)

    source = request.source or get_settings().odds_provider
    try:
        raw_events = _fetch_raw_events(source)
    except (ApiFootballConfigurationError, OddsApiConfigurationError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (ApiFootballRequestError, OddsApiRequestError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    evaluated_markets = [
        evaluate_market(
            event_name=market.event_name,
            market=market.market,
            bankroll=request.bankroll,
            outcomes=market.outcomes,
        )
        for market in normalize_odds_events(raw_events)
    ]
    opportunities = [
        market.to_dict()
        for market in sorted(evaluated_markets, key=lambda item: item.margin, reverse=True)
        if market.is_arbitrage
    ]

    warnings = [
        f"Odds source: {source}.",
        "BTTS is not included in the current Version 1 live scan.",
        "Only complete match winner and over/under 2.5 markets are evaluated.",
    ]

    return ScanResponse(
        mode=source,
        scanned_at=datetime.now(UTC),
        evaluated_market_count=len(evaluated_markets),
        opportunity_count=len(opportunities),
        opportunities=opportunities,
        warnings=warnings,
    )


def _fetch_raw_events(source: str) -> list[dict]:
    if source == "api_football":
        return ApiFootballClient().fetch_epl_odds()
    if source == "the_odds_api":
        return TheOddsApiClient().fetch_epl_odds()

    raise ValueError("source must be one of: api_football, the_odds_api")


def _run_demo_scan(bankroll: float) -> ScanResponse:
    demo_market = evaluate_market(
        event_name="Arsenal vs Chelsea",
        market="match_winner",
        bankroll=bankroll,
        outcomes=[
            OutcomePrice(outcome="Arsenal", bookmaker="DemoBook A", decimal_odds=2.20),
            OutcomePrice(outcome="Draw", bookmaker="DemoBook B", decimal_odds=3.80),
            OutcomePrice(outcome="Chelsea", bookmaker="DemoBook C", decimal_odds=4.00),
        ],
    )

    opportunities = [demo_market.to_dict()] if demo_market.is_arbitrage else []

    return ScanResponse(
        mode="demo",
        scanned_at=datetime.now(UTC),
        evaluated_market_count=1,
        opportunity_count=len(opportunities),
        opportunities=opportunities,
        warnings=["Demo mode uses fixed sample prices and does not call The Odds API."],
    )


@router.get("")
def list_scans() -> dict[str, list]:
    return {"scans": []}


@router.get("/{scan_id}")
def get_scan(scan_id: int) -> dict[str, int | str]:
    return {"scan_id": scan_id, "status": "not_found"}
