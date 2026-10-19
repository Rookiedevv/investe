import { SignalCard } from "@/components/signal-card";
import { Card, H1, H2, Signed } from "@/components/ui";
import { addDays, COMPANY, RULES, todayWarsaw, type Instrument, type PipelineRun, type SignalRow, type Trade } from "@/lib/data";
import { fill, fmtDate, fmtDateTime, fmtNum, fmtSigned } from "@/lib/i18n";
import { requireUser } from "@/lib/session";

type PriceRow = { ticker: string; date: string; close: number };

export default async function SignalsPage() {
  const { supabase, profile, t } = await requireUser();
  const lang = profile.language;
  const since = addDays(todayWarsaw(), -14);

  const [{ data: signals }, { data: runs }, { data: instruments }, { data: prices }, { data: openTrades }] = await Promise.all([
    supabase.from("signals").select("*").returns<SignalRow[]>(),
    supabase.from("pipeline_runs").select("*").order("ran_at", { ascending: false }).limit(1).returns<PipelineRun[]>(),
    supabase.from("instruments").select("*").eq("watched", true).order("sector").order("ticker").returns<Instrument[]>(),
    supabase.from("prices").select("ticker,date,close").gte("date", since).order("date").returns<PriceRow[]>(),
    supabase.from("paper_trades").select("*").is("closed_on", null).returns<Trade[]>(),
  ]);

  const run = runs?.[0];
  const ordered = RULES.map((id) => signals?.find((s) => s.id === id)).filter((s): s is SignalRow => !!s);
  // Active and blocked first, so what needs attention is on top.
  const rank = { active: 0, blocked: 1, watch: 2, idle: 3 };
  ordered.sort((a, b) => rank[a.state] - rank[b.state]);

  const series = new Map<string, PriceRow[]>();
  for (const p of prices ?? []) series.set(p.ticker, [...(series.get(p.ticker) ?? []), p]);
  const last = (tk: string) => {
    const s = series.get(tk) ?? [];
    const a = s.at(-1);
    const b = s.at(-2);
    return a ? { close: a.close, date: a.date, chg: b ? a.close / b.close - 1 : null } : null;
  };

  return (
    <main className="space-y-4">
      <H1>{t.nav.home}</H1>
      <p className="-mt-2 text-sm text-ink-soft">{t.signals.intro}</p>
      {run ? (
        <p className="text-xs text-ink-soft">
          {fill(t.data.asOf, { date: fmtDate(run.as_of ?? run.ran_at, lang) })} · {fill(t.data.updated, { time: fmtDateTime(run.ran_at, lang) })}
          {run.status !== "ok" && <span className="ml-2 font-semibold text-down">{fill(t.data.warning, { msg: run.message })}</span>}
        </p>
      ) : (
        <p className="rounded-xl bg-warn-bg px-4 py-3 text-sm font-semibold">{t.data.none}</p>
      )}

      {ordered.map((row) => (
        <SignalCard key={row.id} row={row} t={t} lang={lang} />
      ))}

      {!!openTrades?.length && (
        <Card>
          <H2>{t.home.openTrades}</H2>
          <ul className="divide-y divide-line">
            {openTrades.map((tr) => {
              const p = last(tr.ticker);
              const ret = p ? p.close / tr.entry_price - 1 : null;
              return (
                <li key={tr.id} className="flex justify-between py-2">
                  <span className="font-semibold">
                    {tr.ticker} <span className="font-normal text-ink-soft">× {tr.shares}</span>
                  </span>
                  <span className="num text-sm">
                    {fmtNum(tr.entry_price, lang)}
                    {p && ` → ${fmtNum(p.close, lang)} `}
                    {ret != null && <Signed value={ret}>({fmtSigned(ret, lang)})</Signed>}
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
              <th className="py-1 text-right font-medium">{t.home.lastClose}</th>
              <th className="py-1 text-right font-medium">{t.home.day}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {(instruments ?? []).map((i) => {
              const p = last(i.ticker);
              return (
                <tr key={i.ticker}>
                  <td className="py-2 pr-2">
                    <span className="font-semibold">{COMPANY[i.ticker] ?? i.name}</span>{" "}
                    <span className="text-xs text-ink-soft">{t.sectors[i.sector]}</span>
                  </td>
                  <td className="num py-2 text-right">{p ? fmtNum(p.close, lang) : <span className="text-sm text-ink-soft">{t.home.noPrices}</span>}</td>
                  <td className="num py-2 text-right text-sm">{p?.chg != null ? <Signed value={p.chg}>{fmtSigned(p.chg, lang)}</Signed> : ""}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>
    </main>
  );
}
