from dataclasses import dataclass
from typing import Protocol


class PricedOutcome(Protocol):
    outcome: str
    bookmaker: str
    decimal_odds: float


@dataclass(frozen=True)
class StakeAllocation:
    outcome: str
    bookmaker: str
    decimal_odds: float
    stake: float
    expected_return: float

    def to_dict(self) -> dict[str, float | str]:
        return {
            "outcome": self.outcome,
            "bookmaker": self.bookmaker,
            "decimal_odds": self.decimal_odds,
            "stake": round(self.stake, 2),
            "expected_return": round(self.expected_return, 2),
        }


def calculate_stakes(
    *,
    outcomes: list[PricedOutcome],
    bankroll: float,
    market_total: float,
) -> list[StakeAllocation]:
    if market_total <= 0:
        raise ValueError("market_total must be greater than zero")

    return [
        StakeAllocation(
            outcome=outcome.outcome,
            bookmaker=outcome.bookmaker,
            decimal_odds=outcome.decimal_odds,
            stake=bankroll * (1 / outcome.decimal_odds) / market_total,
            expected_return=(bankroll * (1 / outcome.decimal_odds) / market_total)
            * outcome.decimal_odds,
        )
        for outcome in outcomes
    ]
