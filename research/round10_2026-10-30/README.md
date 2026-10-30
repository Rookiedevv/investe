# Round 10 (30 Oct 2026): surviving rules as one portfolio (`r10.py`)

**Rules:**
- **Asbis:** monthly sales acceleration > 0, hold until the next release.
- **Results drift:** pre-session report, +3–6% vs WIG20, L1 stocks only, no XTB, hold 21 sessions.
- **Biedronka → Dino:** LFL improved > 0, hold 21 sessions.
- **Car parts:** acceleration > 5 pp, hold until the next release.

**Money management:** the capital is split into K equal slots. A new signal takes a free slot; when all are full, it is skipped. Idle cash earns 5.4%/yr.

**Costs:** per-stock round-trip costs.

**Period:** Feb 2019 – Oct 2026.

**Benchmark:** the WIG20 total-return ETF, bought and held.

| Rules | Slots | Return/yr | ETF | Worst fall | ETF worst fall | Capital invested (avg) | Trades | Years beating ETF |
|---|---|---|---|---|---|---|---|---|
| All four | 3 | 44.9% | 10.9% | −36.4% | −43.7% | 46% | 125 | 6/8 |
| **All four** | **4** | **38.8%** | 10.9% | **−27.6%** | −43.7% | 38% | 136 | 6/8 |
| All four | 5 | 32.6% | 10.9% | −22.2% | −43.7% | 31% | 139 | 6/8 |
| Without car parts | 4/5 | 26–39% | 10.9% | −22 to −36% | −43.7% | 22–35% | ~100 | 6/8 |
| Asbis only | 3 | 21.8% | 10.9% | −36.4% | −43.7% | 18% | 50 | 6/8 |
| Results drift only | 3 | 19.9% | 10.9% | −9.2% | −43.7% | 13% | 36 | 5/8 |
| Car parts only | 3 | 14.4% | 10.9% | −6.0% | −43.7% | 16% | 40 | 5/8 |

**Year by year, all four, 4 slots (%):** 2019 +17.8 (ETF −7.8), 2020 +87.7 (−8.0), 2021 +56.0 (+15.8), 2022 +26.4 (−19.0), 2023 +23.1 (+33.8), 2024 +4.8 (−1.7), 2025 +26.6 (+51.9), 2026 YTD +79.9 (+40.4).

**Average trade net of costs:** results drift +9.7% (35), Asbis +7.9% (50), car parts +5.5% (39), Dino +4.9% (12).

**Read this as an upper bound, not a forecast:**
1. Every rule and threshold was chosen after looking at this same history (in-sample).
2. Asbis and the car-parts companies were studied *because* they had done well.
3. Asbis rose ~120× over the period, and 2020 and 2026 are boom years for it.
4. The worst fall comes from single Asbis trades (−40%).

The money is out of the market about 60% of the time, earning deposit interest. A realistic expectation is far below 39%/yr. The paper trades are the real test.

## Monthly industry data → related stocks (`r10b.py`, data in `industry/`)
**Data:** Eurostat monthly production indices for Poland (2021=100, calendar-adjusted), 2015 – Aug/Sep 2026: hard-coal mining (B05), total industry (B–D) and construction output (F).
- Cement (C2351, C235) and refined petroleum after 2022 are confidential on Eurostat.
- GUS's own pages block automated reading, so GUS data could not be used.

**Entry:** GUS publishes these figures around the 18th–23rd of the following month, so the entry is conservatively the close on or after the 25th. Hold 21 sessions.

**Comparison:** after costs, vs the WIG20 total-return ETF over the same dates.

**Signals:** acceleration = this month's y/y minus the average y/y of the previous 3 months.

| Data → stocks | Best signal | vs ETF | Beats ETF | Verdict |
|---|---|---|---|---|
| Coal output → JSW, Bogdanka | y/y > 0: +2.7 pp; acceleration > 5 pp: +1.6 pp | median −2 to −3 pp | 37–44% | Rejected: the miners lag the ETF in almost every split |
| Construction output → Budimex, Polimex, Mirbud | acceleration > 2 pp: +1.0 pp | median −2.2 | 43% | Rejected |
| Industrial production → KGHM, Orlen, Kęty | acceleration > 2 pp: +0.5 pp | median +1.4 | 57% | Rejected (too small, flips between periods) |
| Car registrations (PZPM, cars + vans, Jan 2019 – Sep 2026, `industry/pzpm_registrations.csv`; entry at the next session after PZPM's publication date) → Inter Cars, Auto Partner | acceleration > 10 pp: +1.5 pp | median −0.1 | 47% (sign flips: +2.5 before 2023, +0.3 after) | Rejected. corr(acceleration, next month) 0.11. The companies' own monthly sales (round 8) remain the better signal |

**Conclusion:** none of the official monthly industry figures predicts the related stocks. Only company-published monthly figures (Asbis, Inter Cars/Auto Partner) have worked.
