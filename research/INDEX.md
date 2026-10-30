# Research index

All research write-ups, raw data and scripts live here; there is no size limit. The claude.ai project "Investing parameters conceptualized" keeps only the small files the scheduled checks update every day (paper trade logs, stock costs, per-sector research notes).

| Path | What |
|---|---|
| `prices/` | Yahoo daily history for ~75 GPW stocks (research only). Add tickers in `prices_tickers.txt`. |
| `project_data/prices_ohlcv.csv` | Bank OHLCV 2018–2026 (Stooq), moved from the claude.ai project on 30 Oct 2026. |
| `xtb_shorts/` | XTB short tests of avoid signals (29 Oct 2026). |
| `wig20_model/` | WIG20 dip predictor and calendar tests (Oct 2026). |
| `round4_2026-10-30/` | Round 4: 52-week-high breakout (lead), momentum (weak), results/dividend run-ups and volume spikes (rejected). |
| `round5_2026-10-30/` | Round 5: zloty, global lag, VIX, sector rotation, turn of year (none pass vs WIG20 ETF). |
| `round6_2026-10-30/` | Round 6: foreign peer results (gaming, e-commerce, copper, oil, CFD brokers, debt collectors, banks, car parts) → Polish stocks. None pass. |
| `round7_2026-10-30/` | Round 7: GUS retail sales and wage releases (surprise vs consensus, acceleration) → retailers, banks, WIG20. None pass. |
| `round8_2026-10-30/` | Round 8: live rules re-checked vs WIG20 ETF (Asbis, results drift, Biedronka→Dino, car parts, PZU). |
| `round9_2026-10-30/` | Round 9: results drift on all pre-session reports (holds; +3–6% band best) and analyst recommendations 2018–26 (no tradable edge; target cuts = weak avoid). |
| `round10_2026-10-30/` | Round 10: surviving rules (Asbis, results drift, Biedronka→Dino, car parts) simulated as one portfolio 2019–26. |
| `round11_2026-10-30/` | Round 11: search for more monthly-sales publishers (none liquid); XTB short leads re-run (Pepco, Eurocash hold; JSW downgraded). |
| `round12_2026-10-30/` | Round 12: results drift by filing time (only pre-session works), negative-reaction shorts, index changes, ABB re-run, turn of month, non-bank sector read-through, drift-rule design variants — all rejected except soft notes on the live rule. |
| `round13_2026-10-30/` | Round 13: bank read-through re-audit vs the ETF on all 2021–26 bank filings (buy side ≈ 0 to +1 pp, fails the bar); tender offers and KNF short register pending web access. |
| `round14_2026-10-30/` | Round 14: quarterly revenue acceleration on 9 liquid companies — no one-month edge (accelerating quarters +1.1 pp, 46%); slow 3-month tilt only. |
| `round15_2026-10-30/` | Round 15: Polish 10-year yield vs banks (sharp 3-month rise → banks lag next month, avoid filter only); web-source status (KNF, SII, tenders). |
| `round16_2026-10-30/` | Round 16: analyst-recommendation aggregates (initiations, consensus, implied upside) — rejected; closes the recommendation family. |
| `round17_2026-10-30/` | Round 17: KNF short-selling register (2,300 rows saved; following or fading disclosed shorts — rejected) and SII sentiment index (806 weeks saved; z ≤ −1.5 contrarian tilt +2.1%/4w, not a rule). |
| `round18_2026-10-30/` | Round 18: futures basis, ETF seasonality, monthly reversal/continuation, drift-rule history conditioning — all rejected; SII-panic + 8% drawdown overlap (+5.3%/4w, n=13) noted as an ETF timing tilt. |
| `round19_2026-10-30/` | Round 19: CHF/PLN, EPOL, coal/gas futures, IPO lock-ups, MSCI review lists (86 events saved). MSCI Standard-addition reversal: XTB short from the effective close +3.7–4.9%, 75–92%, n=12 — short lead pending an execution check; CHF-jump bank short weak; rest rejected. |
| `round20_2026-10-30/` | Round 20: official size and sector indices (bankier, saved). Size rotation among the three Beta ETFs: 6–12m momentum +11%/yr vs WIG20 +4.2% (allocation rule for the ETF leg, not a 1-month trade); sector momentum exists but costs eat it; worst-3-month sector lags 2 pp/month → avoid filter. |
| `prices_foreign/` | Yahoo history for 29 foreign peers (list in `foreign_tickers.txt`). |

New research rounds go in their own dated folder with a `README.md` of results plus the scripts that produced them.
