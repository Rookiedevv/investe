export type Sector = "banks" | "utilities" | "carparts" | "developers" | "index" | "other";

export type Instrument = { ticker: string; name: string; sector: Sector; watched: boolean };

export type EventRow = {
  id: number;
  date: string;
  time: string | null;
  session_timing: string;
  ticker: string;
  sector: string | null;
  category: string;
  event_type: string;
  period: string | null;
  status: "published" | "planned_only" | "scheduled";
  sign: number | null;
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

export type RuleId = "carparts" | "readthrough" | "regime" | "rotation";
export const RULES: RuleId[] = ["carparts", "readthrough", "regime", "rotation"];

export type Stats = { n: number; avg?: number; win_rate?: number; best?: number; worst?: number };

export type BacktestTrade = {
  id: number;
  rule: RuleId;
  ticker: string;
  entry_date: string;
  entry_price: number | null;
  exit_date: string | null;
  exit_price: number | null;
  ret_net: number | null;
  reason: string;
  open: boolean;
};

type OpenTrade = Omit<BacktestTrade, "id" | "rule">;

export type CarpartsCompany = {
  ticker: string;
  period: string;
  release_date: string;
  yoy: number | null;
  accel: number | null;
  signal: boolean;
  entry_date?: string | null;
  entry_price?: number;
  last_close?: number;
  ret_now?: number;
  next_release_est: string;
};

export type Season = {
  period: string;
  early_tickers: string[];
  release_date: string;
  day0: string | null;
  reaction: number | null;
  verdict: "good" | "bad" | "neutral" | "pending";
};

export type SignalData = {
  state: "idle" | "watch" | "active" | "blocked";
  stats: Stats;
  // carparts
  companies?: CarpartsCompany[];
  // readthrough
  last_season?: Season | null;
  next_season?: Season | null;
  schedule?: { ticker: string; date: string }[];
  buy_today?: boolean;
  // regime
  sessions_left?: number;
  bad_event?: string;
  bad_date?: string;
  last_bad?: { date: string; what: string };
  last_good?: { date: string; what: string };
  // shared
  open_trade?: OpenTrade | null;
  last_trade?: OpenTrade;
  ret_now?: number;
  exit_drop?: number;
};

export type SignalRow = { id: RuleId; state: SignalData["state"]; data: SignalData; as_of: string | null; updated_at: string };

export type PipelineRun = { ran_at: string; as_of: string | null; status: string; message: string };

export const COMPANY: Record<string, string> = {
  PKO: "PKO BP", PEO: "Pekao", EBP: "Erste", MBK: "mBank", ING: "ING", MIL: "Millennium", ALR: "Alior",
  BHW: "Handlowy", BNP: "BNP Paribas", PGE: "PGE", TPE: "Tauron", ENA: "Enea", PEP: "Polenergia",
  CAR: "Inter Cars", APR: "Auto Partner", BANKS: "Banki (koszyk)", UTILS: "PGE+Tauron+Enea",
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
