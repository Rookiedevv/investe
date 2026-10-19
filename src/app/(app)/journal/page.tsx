import { closeTrade, deleteTrade, openTrade } from "@/app/actions";
import { Button, Card, ErrorNote, Field, H1, H2, Select, Signed } from "@/components/ui";
import { belka, breakEvenMove, roundTrip } from "@/lib/costs";
import { todayWarsaw, type Instrument, type Trade } from "@/lib/data";
import { fmtDate, fmtMoney, fmtNum, fmtPct } from "@/lib/i18n";
import { requireUser } from "@/lib/session";

export default async function JournalPage({ searchParams }: { searchParams: Promise<{ error?: string; ticker?: string; reason?: string }> }) {
  const { error, ticker: preTicker, reason: preReason } = await searchParams;
  const { supabase, profile, t } = await requireUser();
  const lang = profile.language;
  const tj = t.journal;
  const today = todayWarsaw();

  const [{ data: instruments }, { data: trades }] = await Promise.all([
    supabase.from("instruments").select("*").neq("sector", "index").order("ticker").returns<Instrument[]>(),
    supabase.from("paper_trades").select("*").order("opened_on", { ascending: false }).returns<Trade[]>(),
  ]);
  const open = (trades ?? []).filter((x) => !x.closed_on);
  const closed = (trades ?? []).filter((x) => x.closed_on);

  const year = today.slice(0, 4);
  const yearNet = closed
    .filter((x) => x.closed_on!.startsWith(year))
    .reduce((sum, x) => sum + roundTrip(x.shares, x.entry_price, x.exit_price!).net, 0);

  return (
    <main className="space-y-4">
      <H1>{tj.title}</H1>
      <p className="-mt-2 text-sm text-ink-soft">{tj.note}</p>
      <ErrorNote show={!!error} text={t.error} />

      <Card>
        <H2>{tj.openList}</H2>
        {open.length ? (
          <ul className="divide-y divide-line">
            {open.map((x) => (
              <li key={x.id} className="py-3">
                <div className="flex justify-between">
                  <span className="font-semibold">
                    {x.ticker} <span className="font-normal text-ink-soft">× {x.shares}</span>
                  </span>
                  <span className="num text-sm">
                    {fmtNum(x.entry_price, lang)} · {fmtDate(x.opened_on, lang)}
                  </span>
                </div>
                <p className="text-xs text-ink-soft">
                  {tj.breakEven}: <span className="num">{fmtPct(breakEvenMove(x.shares, x.entry_price), lang)}</span>
                  {x.reason && ` · ${x.reason}`}
                </p>
                <form action={closeTrade} className="mt-2 flex items-end gap-2">
                  <input type="hidden" name="id" value={x.id} />
                  <Field label={tj.closePrice} name="exit_price" type="number" step="0.0001" min="0" required inputMode="decimal" />
                  <Field label={tj.date} name="closed_on" type="date" defaultValue={today} min={x.opened_on} required />
                  <Button type="submit" variant="quiet">
                    {tj.close}
                  </Button>
                </form>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-ink-soft">{tj.empty}</p>
        )}
      </Card>

      <Card>
        <H2>{tj.open}</H2>
        <form action={openTrade} className="grid grid-cols-2 gap-3">
          <Select label={tj.ticker} name="ticker" defaultValue={preTicker}>
            {(instruments ?? []).map((i) => (
              <option key={i.ticker} value={i.ticker}>
                {i.ticker} · {i.name}
              </option>
            ))}
          </Select>
          <Field label={tj.date} name="opened_on" type="date" defaultValue={today} required />
          <Field label={tj.shares} name="shares" type="number" min="1" step="1" required inputMode="numeric" />
          <Field label={tj.price} name="entry_price" type="number" min="0" step="0.0001" required inputMode="decimal" />
          <label className="col-span-2 block text-sm font-medium">
            {tj.reason}
            <textarea name="reason" rows={2} defaultValue={preReason} className="mt-1 block w-full rounded-xl border-2 border-line bg-card px-3 py-2" />
          </label>
          <Button type="submit" className="col-span-2">
            {tj.save}
          </Button>
        </form>
      </Card>

      <Card>
        <H2>{tj.closedList}</H2>
        <div className="mb-3 flex justify-between text-sm">
          <span>
            {tj.yearTotal} {year}: <Signed value={yearNet}>{fmtMoney(yearNet, lang)}</Signed>
          </span>
          <span className="text-ink-soft">
            {tj.belka}: <span className="num">{fmtMoney(belka(yearNet), lang)}</span>
          </span>
        </div>
        {closed.length ? (
          <ul className="divide-y divide-line">
            {closed.map((x) => {
              const r = roundTrip(x.shares, x.entry_price, x.exit_price!);
              return (
                <li key={x.id} className="py-3">
                  <div className="flex justify-between">
                    <span className="font-semibold">
                      {x.ticker} <span className="font-normal text-ink-soft">× {x.shares}</span>
                    </span>
                    <Signed value={r.net}>
                      {fmtMoney(r.net, lang)} ({fmtPct(r.netPct, lang)})
                    </Signed>
                  </div>
                  <p className="num text-xs text-ink-soft">
                    {fmtNum(x.entry_price, lang)} → {fmtNum(x.exit_price!, lang)} · {fmtDate(x.opened_on, lang)} → {fmtDate(x.closed_on!, lang)} ·{" "}
                    {tj.fees} {fmtMoney(r.fees, lang)}
                  </p>
                  <form action={deleteTrade}>
                    <input type="hidden" name="id" value={x.id} />
                    <button className="text-xs text-ink-soft underline">{tj.delete}</button>
                  </form>
                </li>
              );
            })}
          </ul>
        ) : (
          <p className="text-sm text-ink-soft">{tj.empty}</p>
        )}
      </Card>
    </main>
  );
}
