# Round 8 (30 Oct 2026): the live rules re-checked against the WIG20 ETF

**Bar:** each trade is taken after costs and compared with the WIG20 total-return ETF over the same dates, with eMakler fees on the ETF too.
- **Excess:** the vs-ETF result minus what a random hold of the *same stock* for the same length made. This controls for survivorship (today's winners rising anyway).
- **Entry and exit follow each rule:**
  - Car parts and Asbis: buy after the monthly release, sell at the next release.
  - Dino and PZU: hold 21 sessions.

**Data:**
- `asbis_sales.csv` and `biedronka_lfl.csv`, from the claude.ai project files;
- `data/carparts_sales.csv`;
- the results calendar subset in `cal.py`.

**Script:** `r8.py`.

| Rule | n | Net | vs ETF | Median | Beats ETF | <2022 / 2022+ | Same-stock random | **Excess** | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| **Asbis monthly sales acceleration > 0** | 61 | +6.7% | **+6.6 pp** (t 3.7) | +4.1 | **64%** | +8.2 / +4.9 | +3.5 | **+3.1** | Strongest; holds in both periods |
| Asbis acceleration > 5 pp | 44 | +5.2% | +4.7 pp | +4.0 | 66% | +5.3 / +4.0 | +3.2 | +1.4 | Not better than > 0 |
| **Results drift** (pre-session report, +2–6% vs WIG), PZU/Orlen/Pepco/Allegro/Budimex only | 38 | +7.0% | **+4.4 pp** (t 2.6) | +3.5 | **63%** | +8.3 / +2.4 | 0.0 | **+4.4** | Holds; weaker since 2022 |
| **Biedronka LFL improved > 2 pp → Dino** | 8 | +8.3% | **+6.9 pp** (t 2.4) | +8.0 | **75%** | +9.7 / +5.2 | +1.1 | **+5.7** | Strong but only 8 cases |
| Biedronka LFL improved > 0 → Dino | 16 | +4.9% | +2.9 pp | +2.9 | 62% | +4.4 / +1.8 | +1.3 | +1.6 | Weak version |
| Car parts acceleration > 5 pp (CAR + APR) | 45 | +4.7% | +2.8 pp (t 1.9) | +3.0 | 60% | +4.4 / **+1.0** | +0.4 | +2.4 | Fading since 2022 |
| Car parts acceleration > 10 pp | 19 | +4.6% | +4.8 pp | +3.6 | 63% | +5.7 / +2.0 | +0.8 | +3.9 | Few trades |
| PZU results day ≥ +2 pp vs WIG20 | 8 | +7.2% | +2.6 pp | +2.4 | 62% | +1.1 / +3.5 | +0.1 | +2.5 | Weak, few |

The car-parts figures use closes (entry at the close the day after the release, exit at the next release), not the opens in the original test, so they differ slightly from the earlier +6.0% / 47 trades.
