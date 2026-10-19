# Inwestycje

Private investing workbench: daily signals from the rules that survived the research (car-parts sales acceleration, bank early-reporter read-through, bank blackout after bad news, utilities after bank hits), the research event calendar, a findings page, and a paper-trading journal with real eMakler costs. See `SETUP.md` for putting it online.

## Stack
Next.js 16 (App Router) · TypeScript · Tailwind 4 · Supabase (Postgres + RLS, Google auth) · Vercel. Same foundations as Coś ty żarła.

## Layout
- `src/lib/costs.ts`: commission, round-trip result, break-even move, Belka tax (pure functions, tested).
- `src/app/actions.ts`: every write, validated with zod and protected by RLS.
- `src/app/(app)/`: Home, Events, Journal, Settings.
- `src/lib/i18n.ts`: Polish (default) and English text.
- `supabase/migrations/`: schema, RLS and the allow-list sign-up gate.
- `supabase/tests/`: security tests that run on plain Postgres.

## Data model
- `instruments`: 9 banks + 4 utilities (shared, admin-editable).
- `prices`: daily OHLCV, written only by an import job (service role).
- `events`: same columns as the research CSVs (`bank_events.csv`, `util_events.csv`) plus `severity` and `direction`; shared by everyone signed in.
- `paper_trades`: per user, private.

## Commands
```bash
npm run dev        # local dev (needs .env.local, see .env.example)
npm test           # cost engine tests
npm run build
```

Database tests need a local Postgres 16:
```bash
createdb t && psql -d t -f supabase/tests/stub_supabase.sql \
  -f supabase/migrations/20261018000001_init.sql -f supabase/tests/rls_test.sql
```

## Next steps (not built yet)
1. Daily price import (scheduled job → `prices`), then charts per ticker.
2. Import the existing event CSVs into `events`.
3. Event study view: average move and spread-adjusted result after each event type.
4. News feed from Polish and foreign sources.
