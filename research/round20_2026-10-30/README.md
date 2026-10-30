# Round 20 (30 Oct 2026): official index data — size rotation across the three Beta ETFs, sector momentum on WIG sector indices

Data read through the browser from bankier's chart API and saved here: `indices_daily.csv` (WIG20TR from 2012, mWIG40TR and sWIG80TR from 2017-09) and `indices_monthly.csv` (month-end closes: mWIG40 from 1997, sWIG80 from 1994, 15 WIG sector indices from 1996–2022). Everything ends 2 Jan 2026 (bankier's "max period" cap). Stooq works in Chrome for ~45 pages and then shows a captcha, so it is not a bulk source.

## A. Size rotation (`r20a.py`) — an allocation finding, not a 1-month trade
Monthly, 2006–2025 (239 months), price indices with a dividend cushion (WIG20 3.5%/yr, mWIG40/sWIG80 2%/yr), 0.78% charged on each switch, benchmark WIG20 — i.e. the choice between ETFBW20TR, ETFBM40TR and ETFBS80TR, all buyable in eMakler.

| Rule | ann. return | vs WIG20 (+4.2%/yr) | beats WIG20 in | t |
|---|---|---|---|---|
| hold the index with the best past 6 months | **+11.0%** | +0.51 pp/month | 42% of months | 2.2 |
| best past 12 months | +10.5% | +0.47 | 44% | 2.1 |
| best 12-1 | +11.0% | +0.51 | 45% | 2.2 |
| best 3 months | +7.5% | +0.24 | 37% | 1.1 |
| best 1 month | +4.0% | −0.03 | 35% | −0.1 |
| worst 12 months (reversal) | +1.8% | −0.20 | 23% | −1.2 |
| sWIG80 if it beat WIG20 over 6 months, else WIG20 | +10.6% | +0.49 | 32% | 2.2 |
| buy & hold mWIG40 / sWIG80 / equal-weight | +7.9% / **+9.8%** / +7.6% | | | |
| real TR indices 2018-10..2025-12, best 12m | +17.3% vs WIG20TR +9.3% | +0.53 | 53% | 1.5 |

By era (rotation 6m vs WIG20 vs sWIG80): 2006–10 +8.4 / −2.5 / +5.2; 2011–15 +0.6 / −0.4 / +2.6; 2016–20 +8.6 / +6.3 / +0.9; 2021–25 +10.1 / +8.9 / +13.2. Max drawdown −66% for everything (2008). Rotation spends 46% of the time in sWIG80, 29% mWIG40, 25% WIG20, switches ~2×/yr.

**Reading:** the WIG20 ETF has been the worst of the three size ETFs over 20 years (+4.2%/yr vs +9.8% sWIG80); a 6–12-month momentum pick among the three roughly matches holding sWIG80 but avoids its bad stretches (2016–20) and beats every single index in 3 of 4 five-year eras. It fails the "% of months" test because it is a trend-following profile (small frequent lags, large occasional gains). **Not a 1-month strategy; it is a candidate rule for which ETF the idle ETF leg sits in.** Caveats: ETFBM40TR/ETFBS80TR trade ~0.5–2m zł/day; 2026 missing from the data.

## B. Sector momentum / reversal on official sector indices (`r20b.py`, 15 sectors, 2010–2025, vs WIG20 price index)
Before costs: best 3/6/12-month sectors, top 3, +0.6 pp/month, 55–59% of months, t 2.0 — the sector momentum signal exists in survivorship-free data. After 1.25% per switched sector (buying 2–3 stocks per sector) it is +0.0 to +0.4 pp, 50–55%; only "best 6m, top 1" keeps +0.96 pp/month (53%, fading to +0.5 in 2018–25). **Confirms the round-5 rejection** of sector rotation as a 1-month trade.

Sector reversal is strongly negative: **the sector with the worst past 3 months lags WIG20 by 2.0 pp/month (39% of months, t −3.8); worst 1 month −1.2 pp (t −2.4); worst-3 sectors over 3 months −0.8 pp (t −2.7)** — stable in both halves. **Avoid filter:** do not buy names from the sector with the worst 3-month return, however cheap it looks.
