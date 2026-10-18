import Link from "next/link";
import { Card, H1, H2 } from "@/components/ui";
import { addDays, todayWarsaw, type EventRow, type Instrument, type Trade } from "@/lib/data";
import { fmtDate, fmtNum } from "@/lib/i18n";
import { requireUser } from "@/lib/session";

type LastPrice = { ticker: string; date: string; close: number };

export default async function HomePage() {
  const { supabase, profile, t } = await requireUser();
  const lang = profile.language;
  const today = todayWarsaw();

  const [{ data: events }, { data: instruments }, { data: openTrades }] = await Promise.all([
    supabase
      .from("events")
      .select("*")
      .gte("date", today)
      .lte("date", addDays(today, 14))
      .order("date")
      .returns<EventRow[]>(),
    supabase.from("instruments").select("*").eq("watched", true).order("sector").order("ticker").returns<Instrument[]>(),
    supabase.from("paper_trades").select("*").is("closed_on", null).returns<Trade[]>(),
  ]);

  // Latest close per ticker: one small query each keeps it simple for a short watchlist.
  const last = await Promise.all(
    (instruments ?? []).map(async (i) => {
      const { data } = await supabase
        .from("prices")
        .select("ticker,date,close")
        .eq("ticker", i.ticker)
        .order("date", { ascending: false })
        .limit(1)
        .maybeSingle<LastPrice>();
      return [i.ticker, data] as const;
    }),
  );
  const lastBy = new Map(last);

  return (
    <main className="space-y-4">
      <H1>{t.appName}</H1>

      <Card>
        <H2>{t.home.upcoming}</H2>
        {events?.length ? (
          <ul className="divide-y divide-line">
            {events.map((e) => (
              <li key={e.id} className="flex gap-3 py-2">
                <span className="num w-24 shrink-0 text-sm text-ink-soft">{fmtDate(e.date, lang)}</span>
                <span className="w-24 shrink-0 font-semibold">{e.ticker}</span>
                <span className="text-sm">{e.event_type}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-ink-soft">
            <Link href="/events" className="underline">
              {t.home.noUpcoming}
            </Link>
          </p>
        )}
      </Card>

      {!!openTrades?.length && (
        <Card>
          <H2>{t.home.openTrades}</H2>
          <ul className="divide-y divide-line">
            {openTrades.map((tr) => {
              const close = lastBy.get(tr.ticker)?.close;
              return (
                <li key={tr.id} className="flex justify-between py-2">
                  <span className="font-semibold">
                    {tr.ticker} <span className="font-normal text-ink-soft">× {tr.shares}</span>
                  </span>
                  <span className="num text-sm">
                    {fmtNum(tr.entry_price, lang)}
                    {close != null && ` → ${fmtNum(close, lang)}`}
                  </span>
                </li>
              );
            })}
          </ul>
        </Card>
      )}

      <Card>
        <H2>{t.home.watchlist}</H2>
        <table className="w-full text-left">
          <thead className="text-xs text-ink-soft">
            <tr>
              <th className="py-1 font-medium" />
              <th className="py-1 font-medium" />
              <th className="py-1 text-right font-medium">{t.home.lastClose}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {(instruments ?? []).map((i) => {
              const p = lastBy.get(i.ticker);
              return (
                <tr key={i.ticker}>
                  <td className="py-2 pr-2 font-semibold">{i.ticker}</td>
                  <td className="py-2 pr-2 text-sm text-ink-soft">
                    {i.name} · {t.sectors[i.sector]}
                  </td>
                  <td className="num py-2 text-right">
                    {p ? (
                      <>
                        {fmtNum(p.close, lang)}
                        <span className="block text-xs text-ink-soft">{fmtDate(p.date, lang)}</span>
                      </>
                    ) : (
                      <span className="text-sm text-ink-soft">{t.home.noPrices}</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>
    </main>
  );
}
