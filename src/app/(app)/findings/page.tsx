import { Card, H1, H2 } from "@/components/ui";
import { FINDINGS, type Group, type Verdict } from "@/lib/findings";
import { requireUser } from "@/lib/session";

const GROUPS: Group[] = ["carparts", "banks", "utilities", "developers", "rotation", "general"];
const ORDER: Verdict[] = ["works", "promising", "lead", "rejected"];
const STYLE: Record<Verdict, string> = {
  works: "bg-up/15 text-up",
  promising: "bg-accent text-on-accent",
  lead: "bg-warn-bg text-ink",
  rejected: "bg-paper text-ink-soft border border-line",
};

export default async function FindingsPage() {
  const { profile, t } = await requireUser();
  const lang = profile.language;
  const tf = t.findings;

  return (
    <main className="space-y-4">
      <H1>{tf.title}</H1>
      <p className="-mt-2 text-sm text-ink-soft">{tf.intro}</p>
      {GROUPS.map((g) => {
        const items = FINDINGS.filter((f) => f.group === g).sort((a, b) => ORDER.indexOf(a.verdict) - ORDER.indexOf(b.verdict));
        return (
          <Card key={g}>
            <H2>{tf.groups[g]}</H2>
            <ul className="divide-y divide-line">
              {items.map((f, i) => (
                <li key={i} className="py-3">
                  <div className="flex items-start justify-between gap-3">
                    <p className="font-semibold leading-snug">{f[lang].idea}</p>
                    <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-bold ${STYLE[f.verdict]}`}>{tf.verdict[f.verdict]}</span>
                  </div>
                  <p className="mt-1 text-sm text-ink-soft">{f[lang].result}</p>
                </li>
              ))}
            </ul>
          </Card>
        );
      })}
    </main>
  );
}
