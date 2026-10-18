export type Instrument = { ticker: string; name: string; sector: "banks" | "utilities" | "other"; watched: boolean };

export type EventRow = {
  id: number;
  date: string;
  time: string | null;
  session_timing: "before" | "during" | "after" | "unknown";
  ticker: string;
  category: string;
  event_type: string;
  status: "published" | "planned_only" | "scheduled";
  severity: number | null;
  direction: "positive" | "negative" | "mixed" | null;
  description: string;
  source_url: string | null;
};

export type Trade = {
  id: number;
  ticker: string;
  opened_on: string;
  shares: number;
  entry_price: number;
  closed_on: string | null;
  exit_price: number | null;
  reason: string;
};

/** Today's date (YYYY-MM-DD) in Warsaw, where the exchange is. */
export function todayWarsaw(now = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Warsaw" }).format(now);
}

export function addDays(iso: string, days: number): string {
  const d = new Date(`${iso}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

/** Group tickers like ALL_BANKS apply to every instrument in that sector. */
export const GROUPS: Record<string, Instrument["sector"]> = { ALL_BANKS: "banks", ALL_UTILITIES: "utilities" };
