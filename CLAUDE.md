# CLAUDE.md — handover for the investing app

Read this first in every session, plus `AGENTS.md` (Next.js 16 rule), `README.md` and `SETUP.md`.

## What this is
Zuzanna's private investing workbench (template stage). GPW banks + power utilities, event-driven analysis with roughly one-month holding periods, broker mBank eMakler. Polish first, English switchable. Invite-only (Google login + allow-list).

## How data flows
- `data/*.csv`: research event files (banks, utilities, politics, car-parts sales). Add new events here; never ask Zuzanna to type events in.
- `pipeline/` (Python): `fetch_prices.py` (Yahoo; Stooq now blocks bots), `signals.py` (the four rules + backtests), `run.py` (writes to Supabase).
- `.github/workflows/daily-update`: weekdays 16:30 UTC and on every push to `data/` or `pipeline/`. Needs repo secret `SUPABASE_SECRET_KEY`.
- App reads `signals`, `backtest_trades`, `events`, `prices`, `sales_releases`, `pipeline_runs`; users write only `paper_trades` and settings.
- Findings page text lives in `src/lib/findings.ts` (summary of the project's research_log.md).
- Rule checks vs research (Oct 2026): car parts 47 trades +5.2%/68% (research +6.0%/68%); read-through 6 trades +6.2%; regime 10 trades +4.2%.

## Working rules
- Secrets never go in chat or the repo; only in Vercel env vars (`SUPABASE_SECRET_KEY` when the price import is added).
- Migrations in `supabase/migrations/` are run by hand in the Supabase SQL editor, in order. Give the full SQL ready to paste.
- The app shows analysis and paper trades only. Never store broker credentials or place real orders.
- Cost numbers in `src/lib/costs.ts` come from the eMakler tariff as of Oct 2026; re-check when it changes.

## Checks before pushing
`npx tsc --noEmit -p . && npx eslint src && npx vitest run && npx next build`, plus the RLS tests in README.
