# Round 7 (tested 30 Oct 2026): Polish data releases

**Data:** GUS retail sales (real, y/y) and corporate-sector wages (y/y), with market consensus. Monthly releases Feb 2018 – Sep 2026; consensus available from 2019 (`retail_sales.csv`, `wages.csv`, copied from the claude.ai project files `pl_retail_sales_monthly.csv` and `pl_wages_monthly.csv`).

**Trade:** GUS publishes at 10:00, during the session. Entry at the release-day close, hold 21 sessions.

**Comparison:** after costs, vs the WIG20 total-return ETF over the same dates. For WIG20 itself, the ETF is compared with a deposit.

**Signals:**
- surprise = actual − consensus (±1 / ±2 pp);
- acceleration = this month's y/y − the average of the previous 3 months (±2 pp).

**Baskets:** retailers DNP, LPP, PCO, ALE, ZAB, EUR; banks PKO, PEO, MBK, ALR, ING, MIL, EBP, BHW.

**Script:** `r7.py`.

| Release | Signal | Result | Verdict |
|---|---|---|---|
| Retail sales | beat by ≥ 1–2 pp | Retailers *lag* the ETF (−1.9 pp, beat it 25–35%); WIG20 +1.0–1.3 pp vs deposit, 58–65% | Rejected |
| Retail sales | miss by ≥ 1–2 pp | Retailers ≈ ETF. Banks +2.6 pp, 79% (n=14), but −1.0 before 2021 and +3.5 after (the 2022–25 bank rally) | Rejected (regime, no mechanism) |
| Retail sales | acceleration ±2 pp | Retailers ≈ ETF; banks after a slowdown +2.1 pp, 56%, before 2021 ≈ 0 | Rejected |
| Wages | beat by ≥ 1 pp | Banks +2.6 pp, 59%, n=17; retailers −1.2 pp | Rejected (too few, below bar) |
| Wages | miss / acceleration | n = 3–13, nothing consistent | Rejected |

The same-day link between a surprise and retailers' move vs WIG20 is only 0.16–0.22, and nothing drifts afterwards. CPI, PMI and industrial production were not collected: with consumption and wages showing nothing, the prior for them is low, and building their release and consensus history would take ~300 lookups.
