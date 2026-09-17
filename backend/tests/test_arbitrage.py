import pytest

from app.arbitrage.calculator import OutcomePrice, evaluate_market


def test_evaluate_market_detects_arbitrage_and_balances_returns() -> None:
    result = evaluate_market(
        event_name="Arsenal vs Chelsea",
        market="match_winner",
        bankroll=100,
        outcomes=[
            OutcomePrice(outcome="Arsenal", bookmaker="A", decimal_odds=2.20),
            OutcomePrice(outcome="Draw", bookmaker="B", decimal_odds=3.80),
            OutcomePrice(outcome="Chelsea", bookmaker="C", decimal_odds=4.00),
        ],
    )

    assert result.is_arbitrage is True
    assert result.market_total == pytest.approx(0.967703, rel=0.000001)
    assert result.locked_profit == pytest.approx(3.3374, rel=0.0001)

    expected_returns = [stake.expected_return for stake in result.stakes]
    assert max(expected_returns) - min(expected_returns) < 0.01


def test_evaluate_market_rejects_invalid_odds() -> None:
    with pytest.raises(ValueError, match="decimal odds"):
        evaluate_market(
            event_name="Arsenal vs Chelsea",
            market="match_winner",
            bankroll=100,
            outcomes=[
                OutcomePrice(outcome="Arsenal", bookmaker="A", decimal_odds=1.0),
                OutcomePrice(outcome="Chelsea", bookmaker="B", decimal_odds=2.0),
            ],
        )
