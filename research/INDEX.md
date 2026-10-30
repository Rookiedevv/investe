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
| `prices_foreign/` | Yahoo history for 29 foreign peers (list in `foreign_tickers.txt`). |

New research rounds go in their own dated folder with a `README.md` of results plus the scripts that produced them.
