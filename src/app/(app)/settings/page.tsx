import { addAllowedEmail, removeAllowedEmail, setLanguage, signOut } from "@/app/actions";
import { Button, Card, ErrorNote, H1, H2 } from "@/components/ui";
import { requireUser } from "@/lib/session";

type Allowed = { email: string; is_admin: boolean };

export default async function SettingsPage({ searchParams }: { searchParams: Promise<{ error?: string }> }) {
  const { error } = await searchParams;
  const { supabase, profile, t } = await requireUser();
  const ts = t.settings;

  const { data: allowed } = profile.is_admin
    ? await supabase.from("allowed_emails").select("email,is_admin").order("email").returns<Allowed[]>()
    : { data: null };

  return (
    <main className="space-y-4">
      <H1>{ts.title}</H1>
      <ErrorNote show={!!error} text={t.error} />
      <p className="text-sm text-ink-soft">{profile.email}</p>

      <Card>
        <H2>{ts.language}</H2>
        <div className="flex gap-2">
          {(["pl", "en"] as const).map((l) => (
            <form key={l} action={setLanguage}>
              <input type="hidden" name="language" value={l} />
              <Button variant={profile.language === l ? "primary" : "quiet"} aria-pressed={profile.language === l}>
                {l === "pl" ? "Polski" : "English"}
              </Button>
            </form>
          ))}
        </div>
      </Card>

      {allowed && (
        <Card>
          <H2>{ts.allowList}</H2>
          <p className="mb-3 text-sm text-ink-soft">{ts.allowListNote}</p>
          <ul className="mb-3 divide-y divide-line">
            {allowed.map((a) => (
              <li key={a.email} className="flex items-center justify-between py-2 text-sm">
                <span>
                  {a.email} {a.is_admin && <span className="text-xs text-ink-soft">({ts.admin})</span>}
                </span>
                {a.email !== profile.email && (
                  <form action={removeAllowedEmail}>
                    <input type="hidden" name="email" value={a.email} />
                    <button className="text-ink-soft underline">{ts.remove}</button>
                  </form>
                )}
              </li>
            ))}
          </ul>
          <form action={addAllowedEmail} className="flex flex-wrap items-center gap-2">
            <input
              name="email"
              type="email"
              required
              placeholder="name@gmail.com"
              aria-label="Email"
              className="min-h-11 flex-1 rounded-xl border-2 border-line bg-card px-3"
            />
            <label className="flex items-center gap-1 text-sm">
              <input type="checkbox" name="is_admin" /> {ts.admin}
            </label>
            <Button type="submit" variant="quiet">
              {ts.addEmail}
            </Button>
          </form>
        </Card>
      )}

      <form action={signOut}>
        <Button variant="quiet" className="w-full">
          {ts.signOut}
        </Button>
      </form>
    </main>
  );
}
