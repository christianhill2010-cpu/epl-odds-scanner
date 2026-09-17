from app.normalization.markets import normalize_odds_events


def test_normalize_odds_events_selects_best_prices_for_complete_markets() -> None:
    markets = normalize_odds_events(
        [
            {
                "id": "event-1",
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "bookmakers": [
                    {
                        "key": "book_a",
                        "title": "Book A",
                        "markets": [
                            {
                                "key": "h2h",
                                "last_update": "2026-09-17T12:00:00Z",
                                "outcomes": [
                                    {"name": "Arsenal", "price": 2.0},
                                    {"name": "Draw", "price": 3.6},
                                    {"name": "Chelsea", "price": 4.0},
                                ],
                            },
                            {
                                "key": "totals",
                                "outcomes": [
                                    {"name": "Over", "price": 1.9, "point": 2.5},
                                    {"name": "Under", "price": 2.0, "point": 2.5},
                                    {"name": "Over", "price": 2.4, "point": 3.5},
                                    {"name": "Under", "price": 1.6, "point": 3.5},
                                ],
                            },
                        ],
                    },
                    {
                        "key": "book_b",
                        "title": "Book B",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Arsenal", "price": 2.2},
                                    {"name": "Draw", "price": 3.4},
                                    {"name": "Chelsea", "price": 3.8},
                                ],
                            }
                        ],
                    },
                ],
            }
        ]
    )

    by_market = {market.market: market for market in markets}

    assert set(by_market) == {"match_winner", "over_under_2_5"}
    assert by_market["match_winner"].event_name == "Arsenal vs Chelsea"
    assert [outcome.decimal_odds for outcome in by_market["match_winner"].outcomes] == [
        2.2,
        3.6,
        4.0,
    ]
    assert [outcome.outcome for outcome in by_market["over_under_2_5"].outcomes] == [
        "Over",
        "Under",
    ]


def test_normalize_odds_events_supports_books_shape() -> None:
    markets = normalize_odds_events(
        [
            {
                "event_id": "event-1",
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "books": [
                    {
                        "book": "Book A",
                        "market": "h2h",
                        "outcomes": [
                            {"name": "Arsenal", "price": 2.2},
                            {"name": "Draw", "price": 3.8},
                            {"name": "Chelsea", "price": 4.0},
                        ],
                    }
                ],
            }
        ]
    )

    assert len(markets) == 1
    assert markets[0].market == "match_winner"


def test_normalize_odds_events_supports_api_football_shape() -> None:
    markets = normalize_odds_events(
        [
            {
                "fixture": {"id": 123},
                "teams": {
                    "home": {"name": "Arsenal"},
                    "away": {"name": "Chelsea"},
                },
                "update": "2026-09-17T12:00:00Z",
                "bookmakers": [
                    {
                        "name": "Bet365",
                        "bets": [
                            {
                                "name": "Match Winner",
                                "values": [
                                    {"value": "Home", "odd": "2.10"},
                                    {"value": "Draw", "odd": "3.70"},
                                    {"value": "Away", "odd": "4.00"},
                                ],
                            },
                            {
                                "name": "Goals Over/Under",
                                "values": [
                                    {"value": "Over 2.5", "odd": "1.95"},
                                    {"value": "Under 2.5", "odd": "1.95"},
                                ],
                            },
                        ],
                    },
                    {
                        "name": "Betfair",
                        "bets": [
                            {
                                "name": "Match Winner",
                                "values": [
                                    {"value": "Home", "odd": "2.20"},
                                    {"value": "Draw", "odd": "3.60"},
                                    {"value": "Away", "odd": "3.90"},
                                ],
                            }
                        ],
                    },
                ],
            }
        ]
    )

    by_market = {market.market: market for market in markets}

    assert set(by_market) == {"match_winner", "over_under_2_5"}
    assert by_market["match_winner"].event_name == "Arsenal vs Chelsea"
    assert [outcome.outcome for outcome in by_market["match_winner"].outcomes] == [
        "Home",
        "Draw",
        "Away",
    ]
    assert [outcome.decimal_odds for outcome in by_market["match_winner"].outcomes] == [
        2.2,
        3.7,
        4.0,
    ]
