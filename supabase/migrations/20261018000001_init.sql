-- Investing app — template schema
-- Market data (instruments, prices, events) is shared by everyone signed in.
-- Personal data (paper trades) is visible only to its owner.

-- ───────────────────────── Access control ─────────────────────────

create table public.allowed_emails (
  email text primary key check (email = lower(email)),
  is_admin boolean not null default false,
  added_at timestamptz not null default now()
);
alter table public.allowed_emails enable row level security;

create table public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  email text not null,
  display_name text,
  is_admin boolean not null default false,
  language text not null default 'pl' check (language in ('en', 'pl')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table public.profiles enable row level security;

create policy "own profile: read" on public.profiles for select using (id = auth.uid());
create policy "own profile: update" on public.profiles for update using (id = auth.uid())
  with check (id = auth.uid());

create function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce((select is_admin from public.profiles where id = auth.uid()), false);
$$;

-- Users can't promote themselves to admin or change their email.
create function public.protect_profile_fields() returns trigger
language plpgsql as $$
begin
  if auth.uid() is not null and not public.is_admin() then
    new.is_admin := old.is_admin;
    new.email := old.email;
  end if;
  new.updated_at := now();
  return new;
end $$;

create trigger profiles_protect before update on public.profiles
  for each row execute function public.protect_profile_fields();

create policy "admins manage allow-list" on public.allowed_emails for all
  using (public.is_admin()) with check (public.is_admin());

-- Sign-up gate: only allow-listed emails get an account.
create function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  allowed public.allowed_emails;
begin
  select * into allowed from public.allowed_emails where email = lower(new.email);
  if not found then
    raise exception 'EMAIL_NOT_ALLOWED: % is not on the allow-list', new.email
      using errcode = 'P0001';
  end if;

  insert into public.profiles (id, email, display_name, is_admin)
  values (
    new.id,
    lower(new.email),
    coalesce(new.raw_user_meta_data ->> 'full_name', new.raw_user_meta_data ->> 'name', split_part(new.email, '@', 1)),
    allowed.is_admin
  );
  return new;
end $$;

create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- ───────────────────────── Instruments ─────────────────────────

create table public.instruments (
  ticker text primary key check (ticker ~ '^[A-Z0-9_]{2,12}$'),
  name text not null,
  sector text not null check (sector in ('banks', 'utilities', 'other')),
  market text not null default 'GPW',
  watched boolean not null default true
);
alter table public.instruments enable row level security;
create policy "instruments: read" on public.instruments for select to authenticated using (true);
create policy "instruments: admin write" on public.instruments for all
  using (public.is_admin()) with check (public.is_admin());

insert into public.instruments (ticker, name, sector) values
  ('PKO', 'PKO BP', 'banks'),
  ('PEO', 'Bank Pekao', 'banks'),
  ('EBP', 'Erste Bank Polska', 'banks'),
  ('MBK', 'mBank', 'banks'),
  ('ING', 'ING Bank Śląski', 'banks'),
  ('MIL', 'Bank Millennium', 'banks'),
  ('ALR', 'Alior Bank', 'banks'),
  ('BHW', 'Bank Handlowy', 'banks'),
  ('BNP', 'BNP Paribas Bank Polska', 'banks'),
  ('PGE', 'PGE', 'utilities'),
  ('TPE', 'Tauron', 'utilities'),
  ('ENA', 'Enea', 'utilities'),
  ('PEP', 'Polenergia', 'utilities');

-- ───────────────────────── Daily prices ─────────────────────────
-- Filled by an import job (service role). Read-only for users.

create table public.prices (
  ticker text not null references public.instruments (ticker) on delete cascade,
  date date not null,
  open numeric(14,4) not null,
  high numeric(14,4) not null,
  low numeric(14,4) not null,
  close numeric(14,4) not null,
  volume bigint,
  primary key (ticker, date),
  check (low <= high and low > 0)
);
alter table public.prices enable row level security;
create policy "prices: read" on public.prices for select to authenticated using (true);

-- ───────────────────────── Events ─────────────────────────
-- Same columns as the research CSVs (bank_events.csv, util_events.csv).
-- ticker is a real ticker or a group like ALL_BANKS / ALL_UTILITIES.

create table public.events (
  id bigint generated always as identity primary key,
  date date not null,
  time time,
  session_timing text not null default 'unknown'
    check (session_timing in ('before', 'during', 'after', 'unknown')),
  ticker text not null check (ticker ~ '^[A-Z0-9_]{2,16}$'),
  category text not null,
  event_type text not null,
  period text,
  status text not null default 'published'
    check (status in ('published', 'planned_only', 'scheduled')),
  severity smallint check (severity between 1 and 5),
  direction text check (direction in ('positive', 'negative', 'mixed')),
  description text not null default '',
  source_url text,
  created_by uuid references public.profiles (id) on delete set null default auth.uid(),
  created_at timestamptz not null default now()
);
create index on public.events (date desc);
create index on public.events (ticker, date desc);
alter table public.events enable row level security;
create policy "events: read" on public.events for select to authenticated using (true);
create policy "events: add" on public.events for insert to authenticated with check (created_by = auth.uid());
create policy "events: edit own or admin" on public.events for update
  using (created_by = auth.uid() or public.is_admin())
  with check (created_by = auth.uid() or public.is_admin());
create policy "events: delete own or admin" on public.events for delete
  using (created_by = auth.uid() or public.is_admin());

-- ───────────────────────── Paper trades ─────────────────────────

create table public.paper_trades (
  id bigint generated always as identity primary key,
  user_id uuid not null references public.profiles (id) on delete cascade default auth.uid(),
  ticker text not null references public.instruments (ticker),
  opened_on date not null,
  shares integer not null check (shares > 0),
  entry_price numeric(14,4) not null check (entry_price > 0),
  closed_on date,
  exit_price numeric(14,4) check (exit_price is null or exit_price > 0),
  reason text not null default '',
  created_at timestamptz not null default now(),
  check ((closed_on is null) = (exit_price is null)),
  check (closed_on is null or closed_on >= opened_on)
);
create index on public.paper_trades (user_id, opened_on desc);
alter table public.paper_trades enable row level security;
create policy "own trades" on public.paper_trades for all
  using (user_id = auth.uid()) with check (user_id = auth.uid());
