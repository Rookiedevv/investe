import Link from "next/link";
import { Card } from "@/components/ui";
import { COMPANY, type RuleId, type SignalData, type SignalRow } from "@/lib/data";
import { fill, fmtDate, fmtNum, fmtPct, fmtPts, fmtSigned, type Dict, type Lang } from "@/lib/i18n";

const STATE_STYLE: Record<SignalData["state"], string> = {
  idle: "bg-paper text-ink-soft border-line",
  watch: "bg-warn-bg text-ink border-transparent",
  active: "bg-accent text-on-accent border-accent",
  blocked: "bg-down/15 text-down border-transparent",
};

export function SignalCard({ row, t, lang }: { row: SignalRow; t: Dict; lang: Lang }) {
  const d = row.data;
  const ts = t.signals;
  const copy = ts[row.id];
  const lines = describe(row.id, d, t, lang);
  const s = d.stats;

  return (
    <Card className={row.state === "active" ? "border-2 border-accent" : ""}>
      <div className="mb-2 flex items-start justify-between gap-3">
        <h2 className="text-lg font-bold leading-tight">
          {copy.title}
          {row.id === "rotation" && <span className="ml-2 align-middle text-xs font-medium text-ink-soft">({ts.rotation.lead})</span>}
        </h2>
        <span className={`shrink-0 rounded-full border px-3 py-1 text-xs font-bold ${STATE_STYLE[row.state]}`}>{ts.state[row.state]}</span>
      </div>

      <div className="space-y-2">
        {lines.map((l, i) => (
          <p key={i} className={l.strong ? "font-semibold" : "text-sm"}>
            {l.text}
          </p>
        ))}
      </div>

      {row.id === "carparts" &&
        (d.companies ?? [])
          .filter((c) => c.signal && c.entry_price == null)
          .map((c) => (
            <Link
              key={c.ticker}
              href={`/journal?ticker=${c.ticker}&reason=${encodeURIComponent(`${ts.carparts.title}: ${c.period}, ${c.accel ?? ""}`)}`}
              className="mt-3 inline-block rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-on-accent"
            >
              {ts.toJournal}: {COMPANY[c.ticker]}
            </Link>
          ))}

      {row.id === "readthrough" && d.schedule && d.next_season && (
        <details className="mt-3 text-sm">
          <summary className="cursor-pointer text-ink-soft">{ts.readthrough.schedule}</summary>
          <ul className="mt-2 grid grid-cols-2 gap-x-4">
            {d.schedule.map((x) => (
              <li key={x.ticker} className="num flex justify-between">
                <span>{COMPANY[x.ticker] ?? x.ticker}</span>
                <span className="text-ink-soft">{fmtDate(x.date, lang)}</span>
              </li>
            ))}
          </ul>
        </details>
      )}

      <details className="mt-3 text-sm text-ink-soft">
        <summary className="cursor-pointer">{ts.how}</summary>
        <p className="mt-1">{copy.about}</p>
        {(row.id === "readthrough" || row.id === "regime") && <p className="mt-1">{ts.readthrough.basket}</p>}
      </details>

      {s.n > 0 && (
        <p className="mt-3 border-t border-line pt-3 text-xs text-ink-soft">
          {fill(ts.history, {
            n: s.n,
            avg: fmtSigned(s.avg ?? 0, lang),
            win: fmtPct(s.win_rate ?? 0, lang, 0),
            worst: fmtSigned(s.worst ?? 0, lang),
          })}{" "}
          ·{" "}
          <Link href={`/signals/${row.id}`} className="underline">
            {ts.showHistory}
          </Link>
        </p>
      )}
    </Card>
  );
}

type Line = { text: string; strong?: boolean };

function describe(id: RuleId, d: SignalData, t: Dict, lang: Lang): Line[] {
  const ts = t.signals;
  const out: Line[] = [];
  const openLine = () => {
    if (!d.open_trade) return;
    out.push({ text: fill(ts.openSince, { date: fmtDate(d.open_trade.entry_date, lang), ret: fmtSigned(d.ret_now ?? 0, lang) }), strong: true });
    if (d.exit_drop) out.push({ text: fill(ts.exitRule, { drop: fmtPct(d.exit_drop, lang, 1), days: id === "readthrough" ? 20 : 60 }) });
  };

  if (id === "carparts") {
    for (const c of d.companies ?? []) {
      const name = COMPANY[c.ticker] ?? c.ticker;
      out.push({
        text: fill(ts.carparts.line, {
          name,
          period: c.period,
          yoy: c.yoy == null ? "—" : fmtPts(c.yoy, lang).replace(/ (pkt|pts)$/, "%"),
          accel: c.accel == null ? "—" : fmtPts(c.accel, lang),
        }),
      });
      if (c.signal && c.entry_price != null) {
        out.push({
          text: fill(ts.carparts.holding, {
            name,
            date: fmtDate(c.entry_date ?? c.release_date, lang),
            price: fmtNum(c.entry_price, lang),
            ret: fmtSigned(c.ret_now ?? 0, lang),
            next: fmtDate(c.next_release_est, lang),
          }),
          strong: true,
        });
      } else if (c.signal) {
        out.push({
          text: c.entry_date
            ? fill(ts.carparts.buy, { name, date: fmtDate(c.entry_date, lang), next: fmtDate(c.next_release_est, lang) })
            : fill(ts.carparts.buySoon, { name, next: fmtDate(c.next_release_est, lang) }),
          strong: true,
        });
      }
    }
    if (!(d.companies ?? []).some((c) => c.signal)) {
      const next = (d.companies ?? []).map((c) => c.next_release_est).sort()[0];
      if (next) out.push({ text: fill(ts.carparts.idle, { date: fmtDate(next, lang) }), strong: true });
    }
  }

  if (id === "readthrough") {
    const tickers = (s: { early_tickers: string[] }) => s.early_tickers.map((x) => COMPANY[x] ?? x).join(" + ");
    if (d.buy_today && d.last_season) {
      out.push({
        text: fill(ts.readthrough.buyNext, { tickers: tickers(d.last_season), reaction: fmtSigned(d.last_season.reaction ?? 0, lang) }),
        strong: true,
      });
    }
    openLine();
    if (d.next_season && !d.open_trade && !d.buy_today) {
      out.push({
        text: fill(ts.readthrough.watch, {
          period: d.next_season.period,
          date: fmtDate(d.next_season.release_date, lang),
          tickers: tickers(d.next_season),
        }),
        strong: true,
      });
    }
    if (d.last_season) {
      out.push({
        text: fill(ts.readthrough.lastSeason, {
          period: d.last_season.period,
          tickers: tickers(d.last_season),
          reaction: fmtSigned(d.last_season.reaction ?? 0, lang),
          verdict: ts.readthrough.verdict[d.last_season.verdict],
        }),
      });
    }
    if (!d.next_season && !d.open_trade) out.push({ text: ts.readthrough.idle });
  }

  if (id === "regime") {
    if (d.state === "blocked" && d.bad_date) {
      out.push({
        text: fill(ts.regime.blocked, { n: d.sessions_left ?? 0, date: fmtDate(d.bad_date, lang), what: d.bad_event ?? "" }),
        strong: true,
      });
    }
    openLine();
    if (d.state === "idle" && d.last_bad) {
      out.push({ text: fill(ts.regime.idle, { date: fmtDate(d.last_bad.date, lang), what: d.last_bad.what }), strong: true });
    }
    if (d.last_good) out.push({ text: fill(ts.regime.lastGood, { date: fmtDate(d.last_good.date, lang), what: d.last_good.what }) });
  }

  if (id === "rotation") {
    openLine();
    if (!d.open_trade && d.last_trade) {
      out.push({
        text: fill(ts.rotation.idle, { date: fmtDate(d.last_trade.entry_date, lang), ret: fmtSigned(d.last_trade.ret_net ?? 0, lang) }),
        strong: true,
      });
    }
  }
  return out;
}
