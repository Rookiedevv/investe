-- Investe: research-driven data. Events, prices and signals are written only by the nightly job
-- (service role); signed-in users read them.

-- Instruments: car-parts distributors and the WIG index
alter table public.instruments drop constraint instruments_sector_check;
alter table public.instruments add constraint instruments_sector_check
  check (sector in ('banks', 'utilities', 'carparts', 'developers', 'index', 'other'));
insert into public.instruments (ticker, name, sector, watched) values
  ('CAR', 'Inter Cars', 'carparts', true),
  ('APR', 'Auto Partner', 'carparts', true),
  ('WIG', 'WIG (indeks)', 'index', false)
on conflict (ticker) do nothing;

-- Prices: dividend-adjusted close for return calculations
alter table public.prices add column if not exists adj_close numeric(14,4);

-- Events: read-only for users, filled from the research files
alter table public.events drop constraint events_session_timing_check;
alter table public.events add constraint events_session_timing_check
  check (session_timing in ('before', 'during', 'after', 'non_trading_day', 'unknown'));
alter table public.events add column if not exists sign smallint check (sign between -1 and 1);
alter table public.events add column if not exists sector text;
alter table public.events add column if not exists source text not null default 'manual';
create index if not exists events_sector_date on public.events (sector, date desc);
drop policy if exists "events: add" on public.events;
drop policy if exists "events: edit own or admin" on public.events;
drop policy if exists "events: delete own or admin" on public.events;

-- Monthly sales releases (Inter Cars, Auto Partner) with acceleration
create table public.sales_releases (
  ticker text not null references public.instruments (ticker),
  period text not null,
  release_date date not null,
  release_time time,
  sales_pln_m numeric(12,3),
  yoy_pct numeric(8,2),
  accel numeric(8,2),
  primary key (ticker, period)
);
alter table public.sales_releases enable row level security;
create policy "sales: read" on public.sales_releases for select to authenticated using (true);

-- Current status of each rule (one row per rule)
create table public.signals (
  id text primary key,
  state text not null check (state in ('idle', 'watch', 'active', 'blocked')),
  data jsonb not null default '{}'::jsonb,
  as_of date,
  updated_at timestamptz not null default now()
);
alter table public.signals enable row level security;
create policy "signals: read" on public.signals for select to authenticated using (true);

-- Past trades each rule would have made (after 1% costs)
create table public.backtest_trades (
  id bigint generated always as identity primary key,
  rule text not null,
  ticker text not null,
  entry_date date not null,
  entry_price numeric(14,4),
  exit_date date,
  exit_price numeric(14,4),
  ret_net numeric(10,6),
  reason text not null default '',
  open boolean not null default false
);
create index on public.backtest_trades (rule, entry_date desc);
alter table public.backtest_trades enable row level security;
create policy "trades history: read" on public.backtest_trades for select to authenticated using (true);

-- Log of nightly runs, so the app can show how fresh the data is
create table public.pipeline_runs (
  id bigint generated always as identity primary key,
  ran_at timestamptz not null default now(),
  as_of date,
  status text not null,
  message text not null default ''
);
alter table public.pipeline_runs enable row level security;
create policy "runs: read" on public.pipeline_runs for select to authenticated using (true);
