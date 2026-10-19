import Link from "next/link";
import { Card, H1, H2 } from "@/components/ui";
import { COMPANY, todayWarsaw, type EventRow } from "@/lib/data";
import { fmtDate } from "@/lib/i18n";
import { requireUser } from "@/lib/session";

const SECTORS = ["banks", "utilities", "carparts", "politics"] as const;
type SectorFilter = (typeof SECTORS)[number];

export default async function EventsPage({ searchParams }: { searchParams: Promise<{ sector?: string; limit?: string }> }) {
  const sp = await searchParams;
  const sector = SECTORS.includes(sp.sector as SectorFilter) ? (sp.sector as SectorFilter) : undefined;
  const limit = Math.min(Number(sp.limit) || 60, 1000);
  const { supabase, profile, t } = await requireUser();
  const lang = profile.language;
  const tx = t.events;
  const today = todayWarsaw();

  let upQ = supabase.from("events").select("*").gte("date", today).order("date").limit(50);
  let pastQ = supabase.from("events").select("*").lt("date", today).order("date", { ascending: false }).limit(limit);
  if (sector) {
    upQ = upQ.eq("sector", sector);
    pastQ = pastQ.eq("sector", sector);
  }
  const [{ data: upcoming }, { data: past }] = await Promise.all([upQ.returns<EventRow[]>(), pastQ.returns<EventRow[]>()]);
  const qs = (extra: Record<string, string | undefined>) => {
    const p = new URLSearchParams();
    for (const [k, v] of Object.entries({ sector, ...extra })) if (v) p.set(k, v);
    const s = p.toString();
    return s ? `/events?${s}` : "/events";
  };

  return (
    <main className="space-y-4">
      <H1>{tx.title}</H1>
      <p className="-mt-2 text-sm text-ink-soft">{tx.intro}</p>

      <div className="-mx-1 flex gap-2 overflow-x-auto pb-1">
        <Chip href="/events" active={!sector} label={tx.all} />
        {SECTORS.map((s) => (
          <Chip key={s} href={`/events?sector=${s}`} active={sector === s} label={t.sectors[s]} />
        ))}
      </div>

      {!!upcoming?.length && (
        <Card>
          <H2>{tx.upcoming}</H2>
          <EventList events={upcoming} lang={lang} t={t} />
        </Card>
      )}

      <Card>
        <H2>{tx.past}</H2>
        {past?.length ? <EventList events={past} lang={lang} t={t} /> : <p className="text-sm text-ink-soft">{tx.empty}</p>}
        {past?.length === limit && (
          <Link href={qs({ limit: String(limit + 100) })} className="mt-3 block text-center text-sm font-semibold underline">
            {tx.more}
          </Link>
        )}
      </Card>
    </main>
  );
}

function EventList({ events, lang, t }: { events: EventRow[]; lang: "pl" | "en"; t: Awaited<ReturnType<typeof requireUser>>["t"] }) {
  const tx = t.events;
  return (
    <ul className="divide-y divide-line">
      {events.map((e) => {
        const dot = e.sign === 1 ? "bg-up" : e.sign === -1 ? "bg-down" : "bg-line";
        const signLabel = e.sign === 1 ? tx.positive : e.sign === -1 ? tx.negative : tx.neutral;
        return (
          <li key={e.id} className="py-3">
            <div className="flex flex-wrap items-baseline gap-x-2">
              <span className={`inline-block size-2.5 shrink-0 rounded-full ${dot}`} title={signLabel} aria-label={signLabel} />
              <span className="num text-sm text-ink-soft">
                {fmtDate(e.date, lang)}
                {e.time && ` ${e.time.slice(0, 5)}`}
              </span>
              <span className="font-semibold">{COMPANY[e.ticker] ?? e.ticker.replace("ALL_", "").replace("_", " ")}</span>
              <span className="text-xs text-ink-soft">{e.event_type.replaceAll("_", " ")}</span>
              {e.status !== "published" && <span className="rounded bg-warn-bg px-1.5 text-xs">{tx.scheduled}</span>}
            </div>
            {e.description && <p className="mt-1 text-sm">{e.description}</p>}
            {e.source_url && (
              <a href={e.source_url} target="_blank" rel="noreferrer" className="mt-0.5 inline-block text-xs text-ink-soft underline">
                {tx.source}
              </a>
            )}
          </li>
        );
      })}
    </ul>
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
