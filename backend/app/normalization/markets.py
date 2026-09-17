from dataclasses import dataclass

from app.arbitrage.calculator import OutcomePrice

SUPPORTED_MARKETS = {
    "match_winner",
    "over_under_2_5",
}


@dataclass(frozen=True)
class NormalizedMarket:
    event_name: str
    market: str
    outcomes: list[OutcomePrice]


def normalize_odds_events(raw_events: list[dict]) -> list[NormalizedMarket]:
    normalized_markets: list[NormalizedMarket] = []

    for event in raw_events:
        if _is_api_football_event(event):
            normalized_markets.extend(_normalize_api_football_event(event))
            continue

        event_name = _event_name(event)
        grouped_prices: dict[tuple[str, str], OutcomePrice] = {}

        for bookmaker in _bookmakers(event):
            bookmaker_name = bookmaker.get("title") or bookmaker.get("book") or bookmaker.get("key")
            if not bookmaker_name:
                continue

            for market in _markets(bookmaker):
                market_key = market.get("key") or market.get("market")
                canonical_market = _canonical_market(market_key)
                if not canonical_market:
                    continue

                market_last_update = market.get("last_update") or market.get("updated_at")
                for outcome in market.get("outcomes", []):
                    canonical_outcome = _canonical_outcome(canonical_market, outcome)
                    if not canonical_outcome:
                        continue

                    price = outcome.get("price")
                    if not isinstance(price, int | float):
                        continue

                    candidate = OutcomePrice(
                        outcome=canonical_outcome,
                        bookmaker=str(bookmaker_name),
                        decimal_odds=float(price),
                        last_update=market_last_update,
                    )
                    group_key = (canonical_market, canonical_outcome)
                    current_best = grouped_prices.get(group_key)
                    if current_best is None or candidate.decimal_odds > current_best.decimal_odds:
                        grouped_prices[group_key] = candidate

        for market_name, expected_outcomes in _expected_outcomes(event).items():
            outcomes = [
                grouped_prices[(market_name, outcome_name)]
                for outcome_name in expected_outcomes
                if (market_name, outcome_name) in grouped_prices
            ]
            if len(outcomes) == len(expected_outcomes):
                normalized_markets.append(
                    NormalizedMarket(
                        event_name=event_name,
                        market=market_name,
                        outcomes=outcomes,
                    )
                )

    return normalized_markets


def _is_api_football_event(event: dict) -> bool:
    return isinstance(event.get("fixture"), dict) and isinstance(event.get("bookmakers"), list)


def _normalize_api_football_event(event: dict) -> list[NormalizedMarket]:
    event_name = _api_football_event_name(event)
    grouped_prices: dict[tuple[str, str], OutcomePrice] = {}
    expected_outcomes = {
        "match_winner": ["Home", "Draw", "Away"],
        "over_under_2_5": ["Over", "Under"],
    }

    for bookmaker in event.get("bookmakers", []):
        bookmaker_name = bookmaker.get("name")
        if not bookmaker_name:
            continue

        for bet in bookmaker.get("bets", []):
            canonical_market = _api_football_canonical_market(bet.get("name"))
            if not canonical_market:
                continue

            for value in bet.get("values", []):
                canonical_outcome = _api_football_canonical_outcome(
                    canonical_market,
                    value.get("value"),
                )
                if not canonical_outcome:
                    continue

                price = _decimal_price(value.get("odd"))
                if price is None:
                    continue

                candidate = OutcomePrice(
                    outcome=canonical_outcome,
                    bookmaker=str(bookmaker_name),
                    decimal_odds=price,
                    last_update=event.get("update"),
                )
                group_key = (canonical_market, canonical_outcome)
                current_best = grouped_prices.get(group_key)
                if current_best is None or candidate.decimal_odds > current_best.decimal_odds:
                    grouped_prices[group_key] = candidate

    normalized_markets: list[NormalizedMarket] = []
    for market_name, outcomes in expected_outcomes.items():
        prices = [
            grouped_prices[(market_name, outcome)]
            for outcome in outcomes
            if (market_name, outcome) in grouped_prices
        ]
        if len(prices) == len(outcomes):
            normalized_markets.append(
                NormalizedMarket(
                    event_name=event_name,
                    market=market_name,
                    outcomes=prices,
                )
            )

    return normalized_markets


def _api_football_event_name(event: dict) -> str:
    teams = event.get("teams")
    if isinstance(teams, dict):
        home = teams.get("home", {}).get("name") if isinstance(teams.get("home"), dict) else None
        away = teams.get("away", {}).get("name") if isinstance(teams.get("away"), dict) else None
        if home and away:
            return f"{home} vs {away}"

    fixture = event.get("fixture", {})
    fixture_id = fixture.get("id") if isinstance(fixture, dict) else None
    if fixture_id:
        return f"Fixture {fixture_id}"

    return "Unknown event"


def _api_football_canonical_market(name: str | None) -> str | None:
    if name == "Match Winner":
        return "match_winner"
    if name in {"Goals Over/Under", "Over/Under"}:
        return "over_under_2_5"
    return None


def _api_football_canonical_outcome(market: str, value: str | None) -> str | None:
    if not value:
        return None

    if market == "match_winner" and value in {"Home", "Draw", "Away"}:
        return value

    if market == "over_under_2_5":
        normalized = value.strip()
        if normalized in {"Over 2.5", "Over 2.5 Goals"}:
            return "Over"
        if normalized in {"Under 2.5", "Under 2.5 Goals"}:
            return "Under"

    return None


def _decimal_price(value: object) -> float | None:
    try:
        price = float(value)
    except (TypeError, ValueError):
        return None

    if price <= 1:
        return None

    return price


def _bookmakers(event: dict) -> list[dict]:
    bookmakers = event.get("bookmakers")
    if isinstance(bookmakers, list):
        return bookmakers

    books = event.get("books")
    if isinstance(books, list):
        return books

    return []


def _markets(bookmaker: dict) -> list[dict]:
    markets = bookmaker.get("markets")
    if isinstance(markets, list):
        return markets

    if "market" in bookmaker and "outcomes" in bookmaker:
        return [bookmaker]

    return []


def _event_name(event: dict) -> str:
    home_team = event.get("home_team")
    away_team = event.get("away_team")
    if home_team and away_team:
        return f"{home_team} vs {away_team}"

    return str(event.get("event_id") or event.get("id") or "Unknown event")


def _canonical_market(market_key: str | None) -> str | None:
    if market_key in {"h2h", "h2h_3_way"}:
        return "match_winner"
    if market_key == "totals":
        return "over_under_2_5"
    return None


def _canonical_outcome(canonical_market: str, outcome: dict) -> str | None:
    name = outcome.get("name")
    if not name:
        return None

    if canonical_market == "match_winner":
        return str(name)

    if canonical_market == "over_under_2_5":
        point = outcome.get("point")
        if point != 2.5:
            return None
        if name in {"Over", "Under"}:
            return str(name)

    return None


def _expected_outcomes(event: dict) -> dict[str, list[str]]:
    home_team = event.get("home_team")
    away_team = event.get("away_team")
    expected: dict[str, list[str]] = {
        "over_under_2_5": ["Over", "Under"],
    }

    if home_team and away_team:
        expected["match_winner"] = [str(home_team), "Draw", str(away_team)]

    return expected
