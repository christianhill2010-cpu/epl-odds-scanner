from dataclasses import dataclass

from app.arbitrage.staking import StakeAllocation, calculate_stakes


@dataclass(frozen=True)
class OutcomePrice:
    outcome: str
    bookmaker: str
    decimal_odds: float


@dataclass(frozen=True)
class MarketEvaluation:
    event_name: str
    market: str
    market_total: float
    margin: float
    is_arbitrage: bool
    bankroll: float
    locked_profit: float
    outcomes: list[OutcomePrice]
    stakes: list[StakeAllocation]

    def to_dict(self) -> dict:
        return {
            "event_name": self.event_name,
            "market": self.market,
            "market_total": round(self.market_total, 6),
            "margin": round(self.margin, 6),
            "is_arbitrage": self.is_arbitrage,
            "bankroll": round(self.bankroll, 2),
            "locked_profit": round(self.locked_profit, 2),
            "outcomes": [
                {
                    "outcome": outcome.outcome,
                    "bookmaker": outcome.bookmaker,
                    "decimal_odds": outcome.decimal_odds,
                }
                for outcome in self.outcomes
            ],
            "stakes": [stake.to_dict() for stake in self.stakes],
        }


def evaluate_market(
    *,
    event_name: str,
    market: str,
    bankroll: float,
    outcomes: list[OutcomePrice],
) -> MarketEvaluation:
    if bankroll <= 0:
        raise ValueError("bankroll must be greater than zero")
    if len(outcomes) < 2:
        raise ValueError("at least two outcomes are required")
    if any(outcome.decimal_odds <= 1 for outcome in outcomes):
        raise ValueError("decimal odds must be greater than 1")

    market_total = sum(1 / outcome.decimal_odds for outcome in outcomes)
    margin = 1 - market_total
    is_arbitrage = market_total < 1
    stakes = calculate_stakes(outcomes=outcomes, bankroll=bankroll, market_total=market_total)
    locked_profit = min(stake.expected_return for stake in stakes) - bankroll

    return MarketEvaluation(
        event_name=event_name,
        market=market,
        market_total=market_total,
        margin=margin,
        is_arbitrage=is_arbitrage,
        bankroll=bankroll,
        locked_profit=locked_profit,
        outcomes=outcomes,
        stakes=stakes,
    )
