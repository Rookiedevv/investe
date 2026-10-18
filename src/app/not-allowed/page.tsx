import { headers } from "next/headers";
import { signInWithGoogle } from "@/app/actions";
import { getDict, langFromHeader } from "@/lib/i18n";

export default async function NotAllowedPage() {
  const t = getDict(langFromHeader((await headers()).get("accept-language") ?? ""));
  return (
    <main className="mx-auto flex min-h-dvh max-w-md flex-col justify-center px-4 py-12">
      <div className="rounded-3xl border border-line bg-card px-6 py-8">
        <h1 className="text-2xl font-bold">{t.notAllowed.title}</h1>
        <p className="mt-3">{t.notAllowed.body}</p>
        <form action={signInWithGoogle} className="mt-6">
          <button type="submit" className="min-h-12 w-full rounded-xl border-2 border-line px-4 font-semibold hover:bg-paper">
            {t.notAllowed.tryAnother}
          </button>
        </form>
      </div>
    </main>
  );
}
