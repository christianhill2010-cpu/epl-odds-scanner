# EPL Odds Scanner

An on-demand scanner for finding potential arbitrage opportunities on Premier League football markets.

## Version 1 Scope

Version 1 focuses on a reliable manual scanner before adding scheduled monitoring, alerts, or exchange data.

### Included

- Pull current Premier League odds on demand.
- Use The Odds API as the initial odds provider.
- Normalize odds across bookmakers into canonical events, markets, outcomes, and lines.
- Compare the best available price for each outcome.
- Detect arbitrage where the implied probability total is under 100%.
- Show stake sizing for a user-entered bankroll.
- Show locked profit, bookmaker names, timestamps, and risk warnings.
- Persist scan runs and results in SQLite.

### Initial Markets

- Match winner.
- Both teams to score.
- Over/under 2.5 goals.

### Deferred

- Betfair exchange integration.
- Betfair commission and liquidity handling.
- Draw no bet.
- Asian handicap.
- Alternate goal lines.
- Scheduled scans.
- Alerts.
- User accounts.
- Historical reporting.

## Product Design

The first screen should be the scanner itself, not a marketing page.

Core views:

- Scan controls: competition, market filters, bookmaker filters, and a refresh action.
- Opportunities table: match, market, outcomes, best prices, bookmakers, implied probability, profit margin, and last updated time.
- Opportunity detail panel: stake split, expected return, locked profit, source links, and warnings.
- Market comparison view: best available prices per fixture even when no arbitrage exists.

## Arbitrage Logic

Odds should be converted to decimal odds before calculation.

For each outcome:

```txt
implied_probability = 1 / decimal_odds
```

For a complete market:

```txt
market_total = sum(implied_probability for all outcomes)
```

An arbitrage opportunity exists when:

```txt
market_total < 1
```

The margin is:

```txt
margin = 1 - market_total
```

For a chosen bankroll:

```txt
stake_i = bankroll * (1 / odds_i) / market_total
```

Expected return should be approximately equal for every outcome:

```txt
return_i = stake_i * odds_i
locked_profit = return_i - bankroll
```

## Suggested Architecture

The recommended Version 1 stack is a TypeScript web app with a backend API.

Good default:

- Next.js.
- TypeScript.
- Server-side API routes for odds fetching and arbitrage calculation.
- SQLite for persisted scan runs and opportunity history.

Main modules:

- `odds-providers`: fetch raw odds from The Odds API.
- `normalization`: map provider-specific events, markets, outcomes, and lines into canonical values.
- `best-prices`: select the best available price per canonical outcome.
- `arbitrage`: calculate implied totals and identify opportunities.
- `staking`: calculate stake sizing and locked profit.
- `risk-checks`: flag stale odds, missing outcomes, line mismatches, and incomplete markets.

## Data Flow

```txt
User clicks Scan
  -> API fetches EPL odds from The Odds API
  -> Raw odds are normalized
  -> Outcomes are grouped by event and market
  -> Best price is selected for each outcome
  -> Complete markets are checked for arbitrage
  -> Stake sizing and warnings are added
  -> Results are returned to the UI
```

## Risk Warnings

The app should clearly warn that apparent arbitrage can fail because of:

- Odds moving before both bets are placed.
- Bookmaker limits or rejected bets.
- Incorrectly matched markets or lines.
- Rule differences between bookmakers.
- Palpable error corrections.
- Suspended or voided markets.
- API latency or stale odds.

Version 1 should display timestamps prominently and avoid presenting opportunities as guaranteed.

## Build Milestones

1. Scaffold the web app.
2. Add SQLite schema and migrations for scan runs and scan results.
3. Add environment configuration for The Odds API.
4. Implement the odds provider client.
5. Implement canonical market normalization for the three Version 1 markets.
6. Implement best-price selection.
7. Implement arbitrage and staking calculations.
8. Build the scanner UI and opportunity detail panel.
9. Add tests for arbitrage math and normalization.
10. Add risk warnings and stale-data handling.

## Environment Variables

Secrets should not be committed to the repo or written directly in this README.

Use `.env.local` for local development:

```txt
THE_ODDS_API_KEY=
```

Commit an `.env.example` file with variable names only, so the required configuration is documented without exposing real credentials.

Additional provider configuration can be added when Betfair support is introduced.
