/**
 * Trading costs for GPW stocks at mBank eMakler (tariff as of Oct 2026 —
 * verify against the official table before relying on it).
 * Pure functions, no I/O.
 */
export const COSTS = {
  commissionRate: 0.0039, // 0.39% of order value
  commissionMin: 5, // zł per executed order
  belkaTax: 0.19, // on net yearly profit (0 inside IKE/IKZE)
} as const;

/** Commission for one executed order, rounded to grosze. */
export function commission(orderValue: number): number {
  if (orderValue <= 0) return 0;
  return round2(Math.max(orderValue * COSTS.commissionRate, COSTS.commissionMin));
}

export type TradeResult = {
  buyValue: number;
  sellValue: number;
  fees: number;
  /** Profit after both commissions, before tax. */
  net: number;
  /** net as a fraction of buy value incl. buy commission. */
  netPct: number;
};

/** Result of a round trip (buy, then sell). Spread/slippage are already inside the prices. */
export function roundTrip(shares: number, entry: number, exit: number): TradeResult {
  const buyValue = round2(shares * entry);
  const sellValue = round2(shares * exit);
  const fees = round2(commission(buyValue) + commission(sellValue));
  const net = round2(sellValue - buyValue - fees);
  const cost = buyValue + commission(buyValue);
  return { buyValue, sellValue, fees, net, netPct: cost > 0 ? net / cost : 0 };
}

/** Price move needed just to cover both commissions, as a fraction of entry. */
export function breakEvenMove(shares: number, entry: number): number {
  const buy = shares * entry;
  if (buy <= 0) return 0;
  // Solve sell − buy − c(buy) − c(sell) = 0; c(sell) depends on sell, so iterate.
  let sell = buy;
  for (let i = 0; i < 20; i++) sell = buy + commission(buy) + commission(sell);
  return sell / buy - 1;
}

/** Belka tax on a year's summed net result. Losses offset gains; no tax below zero. */
export function belka(yearNet: number, taxFree = false): number {
  return taxFree || yearNet <= 0 ? 0 : Math.round(yearNet * COSTS.belkaTax);
}

function round2(n: number) {
  return Math.round(n * 100) / 100;
}
