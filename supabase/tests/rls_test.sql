-- Run after the migration on the stub database. Any failed assertion aborts with an error.
\set ON_ERROR_STOP 1
grant usage on schema public to authenticated;
grant all on all tables in schema public to authenticated;
grant all on all sequences in schema public to authenticated;

insert into public.allowed_emails values ('owner@example.com', true), ('friend@example.com', false);

-- 1. Sign-up gate
insert into auth.users (id, email, raw_user_meta_data) values
  ('00000000-0000-0000-0000-000000000001', 'Owner@Example.com', '{"full_name":"Owner"}'),
  ('00000000-0000-0000-0000-000000000002', 'friend@example.com', '{}');
do $$ begin
  begin
    insert into auth.users (email) values ('stranger@example.com');
    raise exception 'FAIL: stranger was allowed';
  exception when others then
    if sqlerrm not like 'EMAIL_NOT_ALLOWED%' then raise; end if;
  end;
  assert (select count(*) from public.profiles) = 2, 'two profiles';
  assert (select is_admin from public.profiles where email = 'owner@example.com'), 'owner is admin';
end $$;

-- 2. As the friend
set role authenticated;
select set_config('request.jwt.claim.sub', '00000000-0000-0000-0000-000000000002', false);
do $$ begin
  assert (select count(*) from public.profiles) = 1, 'friend sees only own profile';
  assert (select count(*) from public.allowed_emails) = 0, 'friend cannot read allow-list';
  assert (select count(*) from public.instruments) = 13, 'instruments are shared';
end $$;
update public.profiles set is_admin = true, language = 'en' where id = auth.uid();
do $$ begin
  assert not (select is_admin from public.profiles where id = auth.uid()), 'self-promotion blocked';
  assert (select language from public.profiles where id = auth.uid()) = 'en', 'normal update works';
end $$;
insert into public.paper_trades (ticker, opened_on, shares, entry_price) values ('PKO', current_date, 10, 60);
insert into public.events (date, ticker, category, event_type) values (current_date, 'ALL_BANKS', 'rates', 'nbp_rate_decision');
do $$ begin
  begin
    insert into public.paper_trades (user_id, ticker, opened_on, shares, entry_price)
      values ('00000000-0000-0000-0000-000000000001', 'PKO', current_date, 1, 1);
    raise exception 'FAIL: wrote a trade for someone else';
  exception when insufficient_privilege then null;
  end;
  begin
    insert into public.instruments (ticker, name, sector) values ('XYZ', 'x', 'other');
    raise exception 'FAIL: non-admin added an instrument';
  exception when insufficient_privilege then null;
  end;
  begin
    insert into public.prices (ticker, date, open, high, low, close) values ('PKO', current_date, 1, 1, 1, 1);
    raise exception 'FAIL: user wrote prices';
  exception when insufficient_privilege then null;
  end;
end $$;

-- 3. As the owner: sees shared events, not the friend's trades, can't delete the friend's event
select set_config('request.jwt.claim.sub', '00000000-0000-0000-0000-000000000001', false);
do $$ begin
  assert (select count(*) from public.paper_trades) = 0, 'owner cannot see friend trades';
  assert (select count(*) from public.events) = 1, 'events are shared';
  assert (select count(*) from public.allowed_emails) = 2, 'admin reads allow-list';
end $$;
delete from public.paper_trades;
reset role;
do $$ begin
  assert (select count(*) from public.paper_trades) = 1, 'friend trade survived owner delete';
end $$;

\echo 'ALL RLS TESTS PASSED'
