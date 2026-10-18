import Link from "next/link";
import { addEvent, deleteEvent } from "@/app/actions";
import { Button, Card, ErrorNote, Field, H1, H2, Select } from "@/components/ui";
import { GROUPS, todayWarsaw, type EventRow, type Instrument } from "@/lib/data";
import { fmtDate } from "@/lib/i18n";
import { requireUser } from "@/lib/session";

const CATEGORIES = ["bank_results", "company_results", "rates", "sector_shock", "politics", "other"];

export default async function EventsPage({ searchParams }: { searchParams: Promise<{ ticker?: string; error?: string }> }) {
  const { ticker, error } = await searchParams;
  const { supabase, profile, t } = await requireUser();
  const lang = profile.language;
  const tx = t.events;

  const { data: instruments } = await supabase.from("instruments").select("*").order("ticker").returns<Instrument[]>();
  const tickers = [...Object.keys(GROUPS), ...(instruments ?? []).map((i) => i.ticker)];

  let q = supabase.from("events").select("*").order("date", { ascending: false }).limit(200);
  if (ticker) {
    // A company's list also shows events for its whole sector (e.g. ALL_BANKS).
    const sector = instruments?.find((i) => i.ticker === ticker)?.sector;
    const group = Object.entries(GROUPS).find(([, s]) => s === sector)?.[0];
    q = q.in("ticker", group ? [ticker, group] : [ticker]);
  }
  const { data: events } = await q.returns<EventRow[]>();

  const dirLabel = (d: EventRow["direction"]) => (d ? tx[d] : tx.none);

  return (
    <main className="space-y-4">
      <H1>{tx.title}</H1>
      <ErrorNote show={!!error} text={t.error} />

      <div className="-mx-1 flex gap-2 overflow-x-auto pb-1">
        <Chip href="/events" active={!ticker} label={tx.all} />
        {tickers.map((tk) => (
          <Chip key={tk} href={`/events?ticker=${tk}`} active={ticker === tk} label={tk} />
        ))}
      </div>

      <Card>
        {events?.length ? (
          <ul className="divide-y divide-line">
            {events.map((e) => (
              <li key={e.id} className="py-3">
                <div className="flex flex-wrap items-baseline gap-x-3">
                  <span className="num text-sm text-ink-soft">
                    {fmtDate(e.date, lang)}
                    {e.time && ` ${e.time.slice(0, 5)}`}
                  </span>
                  <span className="font-semibold">{e.ticker}</span>
                  <span className="text-sm">{e.event_type}</span>
                  {e.severity && <span className="text-xs text-ink-soft">● {e.severity}/5</span>}
                  <span className={`text-xs ${e.direction === "positive" ? "text-up" : e.direction === "negative" ? "text-down" : "text-ink-soft"}`}>
                    {dirLabel(e.direction)}
                  </span>
                </div>
                {e.description && <p className="mt-1 text-sm text-ink-soft">{e.description}</p>}
                <div className="mt-1 flex gap-4 text-xs">
                  {e.source_url && (
                    <a href={e.source_url} target="_blank" rel="noreferrer" className="underline">
                      {tx.source}
                    </a>
                  )}
                  <form action={deleteEvent}>
                    <input type="hidden" name="id" value={e.id} />
                    <button className="text-ink-soft underline">{tx.delete}</button>
                  </form>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-ink-soft">{tx.empty}</p>
        )}
      </Card>

      <Card>
        <H2>{tx.add}</H2>
        <form action={addEvent} className="grid grid-cols-2 gap-3">
          <Field label={tx.date} name="date" type="date" required defaultValue={todayWarsaw()} />
          <Field label={tx.time} name="time" type="time" />
          <Select label={tx.ticker} name="ticker" defaultValue={ticker ?? "ALL_BANKS"}>
            {tickers.map((tk) => (
              <option key={tk}>{tk}</option>
            ))}
          </Select>
          <Select label={tx.session} name="session_timing" defaultValue="unknown">
            <option value="before">before</option>
            <option value="during">during</option>
            <option value="after">after</option>
            <option value="unknown">unknown</option>
          </Select>
          <Select label={tx.category} name="category" defaultValue="sector_shock">
            {CATEGORIES.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </Select>
          <Field label={tx.type} name="event_type" required placeholder="chf_ruling" />
          <Select label={tx.severity} name="severity" defaultValue="">
            <option value="">{tx.none}</option>
            {[1, 2, 3, 4, 5].map((n) => (
              <option key={n}>{n}</option>
            ))}
          </Select>
          <Select label={tx.direction} name="direction" defaultValue="">
            <option value="">{tx.none}</option>
            <option value="positive">{tx.positive}</option>
            <option value="negative">{tx.negative}</option>
            <option value="mixed">{tx.mixed}</option>
          </Select>
          <Select label="Status" name="status" defaultValue="published">
            <option value="published">published</option>
            <option value="scheduled">scheduled</option>
            <option value="planned_only">planned_only</option>
          </Select>
          <Field label={tx.source} name="source_url" type="url" />
          <label className="col-span-2 block text-sm font-medium">
            {tx.description}
            <textarea name="description" rows={3} className="mt-1 block w-full rounded-xl border-2 border-line bg-card px-3 py-2" />
          </label>
          <Button type="submit" className="col-span-2">
            {tx.save}
          </Button>
        </form>
      </Card>
    </main>
  );
}

function Chip({ href, active, label }: { href: string; active: boolean; label: string }) {
  return (
    <Link
      href={href}
      className={`shrink-0 rounded-full border px-3 py-1 text-sm font-semibold ${active ? "border-accent bg-accent text-on-accent" : "border-line bg-card"}`}
    >
      {label}
    </Link>
  );
}
