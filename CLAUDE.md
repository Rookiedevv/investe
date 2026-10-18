# CLAUDE.md — handover for the investing app

Read this first in every session, plus `AGENTS.md` (Next.js 16 rule), `README.md` and `SETUP.md`.

## What this is
Zuzanna's private investing workbench (template stage). GPW banks + power utilities, event-driven analysis with roughly one-month holding periods, broker mBank eMakler. Polish first, English switchable. Invite-only (Google login + allow-list).

## Working rules
- Secrets never go in chat or the repo; only in Vercel env vars (`SUPABASE_SECRET_KEY` when the price import is added).
- Migrations in `supabase/migrations/` are run by hand in the Supabase SQL editor, in order. Give the full SQL ready to paste.
- The app shows analysis and paper trades only. Never store broker credentials or place real orders.
- Cost numbers in `src/lib/costs.ts` come from the eMakler tariff as of Oct 2026; re-check when it changes.

## Checks before pushing
`npx tsc --noEmit -p . && npx eslint src && npx vitest run && npx next build`, plus the RLS tests in README.
