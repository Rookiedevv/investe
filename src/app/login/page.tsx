import { headers } from "next/headers";
import { signInWithGoogle } from "@/app/actions";
import { getDict, langFromHeader } from "@/lib/i18n";

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ error?: string }> }) {
  const { error } = await searchParams;
  const t = getDict(langFromHeader((await headers()).get("accept-language") ?? ""));

  return (
    <main className="mx-auto flex min-h-dvh max-w-md flex-col justify-center px-4 py-12">
      <div className="rounded-3xl border border-line bg-card px-6 py-10">
        <h1 className="text-5xl font-bold tracking-tight">{t.appName}</h1>
        <p className="mt-4 text-lg text-ink-soft">{t.login.tagline}</p>
        <form action={signInWithGoogle} className="mt-8">
          <button
            type="submit"
            className="flex min-h-14 w-full items-center justify-center gap-3 rounded-xl bg-accent px-4 text-lg font-semibold text-on-accent hover:opacity-90"
          >
            <svg aria-hidden viewBox="0 0 24 24" className="size-5" fill="currentColor">
              <path d="M21.35 11.1H12v2.9h5.35c-.25 1.5-1.7 4.4-5.35 4.4-3.2 0-5.85-2.65-5.85-5.9S8.8 6.6 12 6.6c1.85 0 3.05.8 3.75 1.45l2.55-2.45C16.7 4.1 14.55 3.2 12 3.2 7.15 3.2 3.2 7.15 3.2 12s3.95 8.8 8.8 8.8c5.1 0 8.45-3.55 8.45-8.6 0-.6-.05-1.05-.1-1.1z" />
            </svg>
            {t.login.google}
          </button>
        </form>
        {error && <p className="mt-3 text-sm font-semibold text-down">{t.login.failed}</p>}
        <p className="mt-6 text-sm text-ink-soft">{t.login.privateNote}</p>
      </div>
    </main>
  );
}
