"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const icons = {
  home: <path d="M4 11l8-7 8 7v9H4zM9 20v-6h6v6" />,
  events: <path d="M5 5h14v15H5zM5 10h14M9 3v4M15 3v4" />,
  journal: <path d="M4 18l5-6 4 3 7-9M4 21h16" />,
  settings: <path d="M4 7h10M18 7h2M4 17h4M12 17h8M14 4v6M8 14v6" />,
};

export type NavLabels = Record<keyof typeof icons, string>;

export function BottomNav({ labels }: { labels: NavLabels }) {
  const path = usePathname();
  const tabs: [string, keyof typeof icons][] = [
    ["/", "home"],
    ["/events", "events"],
    ["/journal", "journal"],
    ["/settings", "settings"],
  ];
  return (
    <nav className="fixed inset-x-0 bottom-0 z-20 border-t border-line bg-card pb-[env(safe-area-inset-bottom)]">
      <div className="mx-auto flex max-w-2xl px-2">
        {tabs.map(([href, name]) => {
          const active = href === "/" ? path === "/" : path.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              aria-current={active ? "page" : undefined}
              className={`flex flex-1 flex-col items-center gap-0.5 py-2 text-xs font-semibold ${active ? "text-accent" : "text-ink-soft"}`}
            >
              <svg aria-hidden viewBox="0 0 24 24" className="size-6" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                {icons[name]}
              </svg>
              {labels[name]}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
