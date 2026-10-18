import { describe, expect, it } from "vitest";
import { belka, breakEvenMove, commission, roundTrip } from "./costs";

describe("commission", () => {
  it("applies the 5 zł minimum to small orders", () => {
    expect(commission(500)).toBe(5);
    expect(commission(1000)).toBe(5);
  });
  it("charges 0.39% above roughly 1,282 zł", () => {
    expect(commission(10_000)).toBe(39);
  });
  it("is zero for an empty order", () => {
    expect(commission(0)).toBe(0);
  });
});

describe("roundTrip", () => {
  it("subtracts both commissions", () => {
    const r = roundTrip(100, 100, 105); // 10,000 → 10,500
    expect(r.fees).toBe(39 + 40.95);
    expect(r.net).toBe(500 - 79.95);
  });
  it("shows a loss on a flat trade", () => {
    expect(roundTrip(10, 50, 50).net).toBe(-10);
  });
});

describe("breakEvenMove", () => {
  it("is about 0.78% for a large order", () => {
    expect(breakEvenMove(100, 100)).toBeCloseTo(0.00783, 4);
  });
  it("is much larger for a tiny order", () => {
    expect(breakEvenMove(5, 100)).toBeGreaterThan(0.019);
  });
  it("leaves a round trip at zero net", () => {
    const move = breakEvenMove(100, 100);
    expect(Math.abs(roundTrip(100, 100, 100 * (1 + move)).net)).toBeLessThan(0.02);
  });
});

describe("belka", () => {
  it("taxes net profit at 19%", () => {
    expect(belka(1000)).toBe(190);
  });
  it("is zero for losses and tax-free accounts", () => {
    expect(belka(-500)).toBe(0);
    expect(belka(1000, true)).toBe(0);
  });
});
