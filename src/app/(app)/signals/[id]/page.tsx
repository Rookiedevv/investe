import Link from "next/link";
import { notFound } from "next/navigation";
import { Card, H1, Signed } from "@/components/ui";
import { COMPANY, RULES, type BacktestTrade, type RuleId } from "@/lib/data";
import { fmtDate, fmtNum, fmtSigned } from "@/lib/i18n";
import { requireUser } from "@/lib/session";

export default async function RuleHistoryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!RULES.includes(id as RuleId)) notFound();
  const { supabase, profile, t } = await requireUser();
  const lang = profile.language;
  const ts = t.signals;

  const { data: trades } = await supabase
    .from("backtest_trades")
    .select("*")
    .eq("rule", id)
    .order("entry_date", { ascending: false })
    .returns<BacktestTrade[]>();

  const isBasket = id !== "carparts";

  return (
    <main className="space-y-4">
      <Link href="/" className="text-sm text-ink-soft underline">
        ← {ts.back}
      </Link>
      <H1>{ts[id as RuleId].title}</H1>
      <p className="-mt-2 text-sm text-ink-soft">{ts[id as RuleId].about}</p>
      {isBasket && <p className="text-xs text-ink-soft">{ts.basketNote}</p>}

      <Card>
        <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-ink-soft">{ts.historyTitle}</h2>
        {trades?.length ? (
          <ul className="divide-y divide-line">
            {trades.map((x) => (
              <li key={x.id} className="py-3">
                <div className="flex items-baseline justify-between gap-3">
                  <span className="font-semibold">{COMPANY[x.ticker] ?? x.ticker}</span>
                  {x.open || x.ret_net == null ? (
                    <span className="text-sm text-ink-soft">{ts.open}</span>
                  ) : (
                    <Signed value={x.ret_net}>{fmtSigned(x.ret_net, lang)}</Signed>
                  )}
                </div>
                <p className="num text-xs text-ink-soft">
                  {ts.entry} {fmtDate(x.entry_date, lang)}
                  {x.entry_price != null && ` (${fmtNum(x.entry_price, lang)})`}
                  {x.exit_date && ` → ${ts.exit} ${fmtDate(x.exit_date, lang)}`}
                  {x.exit_price != null && ` (${fmtNum(x.exit_price, lang)})`}
                </p>
                {x.reason && <p className="mt-0.5 text-xs">{x.reason}</p>}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-ink-soft">{ts.noTrades}</p>
        )}
      </Card>
    </main>
  );
}
