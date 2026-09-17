from datetime import UTC, datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.arbitrage.calculator import OutcomePrice, evaluate_market

router = APIRouter(prefix="/scans", tags=["scans"])


class ScanRequest(BaseModel):
    bankroll: float = Field(default=100.0, gt=0)


class ScanResponse(BaseModel):
    mode: str
    scanned_at: datetime
    opportunity_count: int
    opportunities: list[dict]
    warnings: list[str]


@router.post("", response_model=ScanResponse)
def run_scan(request: ScanRequest) -> ScanResponse:
    # Demo prices let us exercise the API and math before the live odds provider is wired.
    demo_market = evaluate_market(
        event_name="Arsenal vs Chelsea",
        market="match_winner",
        bankroll=request.bankroll,
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
        opportunity_count=len(opportunities),
        opportunities=opportunities,
        warnings=["Live odds provider is not wired yet; this endpoint currently returns demo data."],
    )


@router.get("")
def list_scans() -> dict[str, list]:
    return {"scans": []}


@router.get("/{scan_id}")
def get_scan(scan_id: int) -> dict[str, int | str]:
    return {"scan_id": scan_id, "status": "not_found"}
