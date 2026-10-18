import { BottomNav } from "@/components/bottom-nav";
import { requireUser } from "@/lib/session";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const { profile, t } = await requireUser();
  return (
    <>
      <div lang={profile.language} className="mx-auto max-w-2xl px-4 pt-[max(1rem,env(safe-area-inset-top))] pb-28">
        {children}
      </div>
      <BottomNav labels={t.nav} />
    </>
  );
}
