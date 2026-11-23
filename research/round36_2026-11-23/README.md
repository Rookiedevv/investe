# Round 36 (23 Nov 2026): liquid cohorts, stored results, factor search

Zuzanna asked to group the liquid GPW shares into cohorts, download and store their results over time, look for a factor worth paper-trading and schedule its check.

**Outcome in one line:** one factor family survives, growth + trend. Its five best stocks beat WIG by about 1 pp a month after costs, in 56% of months. That is a paper-trade lead, not a rule. The worst fifth on the same score lags in 15 of 16 years and becomes an avoid list. Value, quality, dividend yield, low volatility and size show nothing.

## 1. Data now stored

| What | Where | Coverage |
|---|---|---|
| Daily prices (Yahoo, dividend-adjusted) | `research/prices/<T>.csv` | 170 tickers requested, 149 with data, back to Nov 2009 (was 2014) |
| Quarterly income statement, balance sheet, cash flow, share count | `research/fundamentals/{income,balance,cashflow,market}_q.csv` | 85 companies, 5,474 company-quarters, most from 2005–2007; every line of the statement; `pub_date` = day the periodic report was published |
| Raw tables as downloaded | `research/fundamentals/raw/*.html.gz` | same 85 |
| Ticker → biznesradar page name | `research/fundamentals/names.csv` | |
| Cohort table (sector, turnover, cost, score) | `output/liquid_cohorts.csv` | 62 stocks with ≥ 1m zł/day |

Source of the statements: biznesradar.pl quarterly report pages (`<page>/<NAME>,Q`; the ticker form redirects to the yearly table, which is why earlier rounds got yearly data for most companies). The site stopped answering after a few hundred quick requests, so the download covers the 85 names that matter (every stock that has ever been liquid, except short spells of ML System and Mirbud) and not the 60 illiquid ones. The fetcher now goes one page at a time with a pause.

## 2. Cohorts (60-day median turnover, 20 Nov 2026)

| Cohort | Stocks | Round-trip cost |
|---|---|---|
| Large, ≥ 30m zł/day | 17 | 0.9% |
| Mid, 10–30m | 10 | 1.0% |
| Small-liquid, 2–10m | 21 | 1.3–2.0% |
| Watch, 1–2m (not traded) | 14 | 2.0% |

Liquid stocks (≥ 2m) by sector: retail/consumer 10, banks 9, oil/mining/chemicals 5, IT 5, finance 4, industrials 4, utilities 3, construction 2, telecom/media 2, health 2, gaming 1, developers 1. The liquid universe was 20 stocks in 2012, 27 in 2018, 42 in 2021 and 48 today.

## 3. Method

Every month-end from Jan 2011 to Oct 2026 (190 months): rank the liquid stocks (about 29 on average) on a factor using only what was known at that close, buy the best fifth (and, separately, the best 5) at the close, sell at the next month-end close. Each stock pays its full round-trip cost every month. WIG is the total-return proxy from round 34 less the ETF's 0.78% round trip. Statements count only when the periodic report was published before the ranking day and no more than 150 days earlier.

Two comparisons are shown: against WIG (her bar) and against the average liquid stock on the same dates (which removes most of the survivorship bias, because the stock list is today's survivors).

## 4. Results by factor family (best fifth, pp per month)

| Family | Factor | vs average stock | vs WIG | Months ahead of WIG |
|---|---|---|---|---|
| Value | earnings/price | −0.3 | −0.5 | 38% |
| | book/price | −0.4 | −0.7 | 45% |
| | sales/price, cash flow/price, EBITDA/EV | −0.1 to −0.4 | −0.4 to −0.7 | 40–44% |
| | dividend yield | −0.4 | −0.7 (t −3.0) | 40% |
| Quality | ROE, ROA, margins, accruals, leverage, F-score | −0.3 to +0.2 | −0.6 to 0.0 | 42–48% |
| Size / liquidity | small cap, low turnover, Amihud | −0.3 to −0.6 | −0.5 to −0.9 | 33–37% |
| Risk | low volatility, low beta, no-lottery | −0.2 to +0.2 | −0.5 to 0.0 | 43–52% |
| Reversal | last month's / last week's losers | −0.5 | −0.8 | 36–38% |
| **Trend** | 12-1 momentum ÷ volatility | **+1.3** (t 3.0) | +1.0 | 50% |
| | 12-1, 6-1, 6, 3 month momentum | +1.3 | +1.0 | 48–54% |
| | near 52-week high | +1.0 | +0.7 | 53% |
| **Profit growth** | quarter's net profit change y/y ÷ equity (`d_ni`) | **+1.3** (t 3.0) | +1.1 | 50% |
| | same ÷ its own variability (`sue`) | +1.1 (t 2.8) | +0.9 | 49% |
| | EBIT change, margin change, revenue growth | +0.7 to +1.1 | +0.5 to +0.8 | 44–51% |

Trend and profit growth are the only families where the best fifth beats the average stock in both halves of the sample and the worst fifth loses by a similar amount. Neither alone beats WIG in more than about half of the months.

## 5. The lead: growth + trend ("G+M")

Score = average percentile rank of four things (at least three must be present): `d_ni`, `sue`, 12-1 momentum ÷ volatility, closeness to the 52-week high. Definition in `gm36.py`.

| | vs average stock | vs WIG | Months ahead of WIG |
|---|---|---|---|
| Best fifth | +1.5 pp (t 3.8) | +1.25 pp (t 2.7) | 56% |
| **Best 5 stocks** | +1.5 pp (t 3.4) | **+1.3 pp; +0.95 with months capped at ±15 pp; median +0.6** | **56%** |
| Worst fifth | **−1.4 pp (t −4.0)** | | below the average stock in 15 of 16 years |
| Middle three fifths | −0.2 to +0.1 | | |

- Both halves hold: best 5 vs WIG +0.9 pp (2011–18) and +1.7 pp (2019–26). By thirds: +0.6, +2.7, +0.7.
- Entry one session later: +1.2 pp, 55%. Held two months: +2.3 pp; three months: +3.3 pp (59%). The effect is slow, so the exact day matters little.
- Shuffling the scores among stocks 200 times never got above t 2.0 (real: 3.8) or above +0.7 pp for the best 5 (real: +1.3).
- Dropping any one of the four parts leaves +0.9 to +1.2 pp vs WIG.
- On average only 1.5 of the 5 names change each month, so real costs are lower than charged here.

**Weak points**
1. Half of the months still lose to WIG. Best 5 beat both WIG and a deposit (0.45%) in only 39% of months. Per year the best 5 beat WIG in 10 of 16 years; 2011, 2012, 2014, 2017, 2018 and 2025 were negative.
2. It does not work among the largest stocks (≥ 30m zł/day, best 3: −0.6 pp). It lives in the 2–30m names (best 3 of the mid cohort +1.3, of the small-liquid cohort +1.4).
3. One month (June 2020, Mercator +) adds 0.4 pp to the mean; the capped figure is the honest one.
4. About 60 factor variants were tried in this round. A t of 3.8 against the average stock survives that; the t of 2.7 against WIG is not strong after so many tries.
5. Today's stock list. Delisted names (Energa, Lotos, PGNiG, Play, Ciech) are missing. The comparison with the average stock on the same dates is the one to trust.
6. Statements are as shown today, so later restatements are in; publication dates are those of the full report, later than preliminary releases.

**Event version rejected.** Buying the day after a strong report and holding 21 sessions (`ev36.py`, 1,860 reports): SUE ≥ 1 → +0.6 pp vs WIG, 50%; SUE ≥ 2 → +1.3 pp, 53%, negative before 2019. The existing results-drift rule (price reaction +3–6%) is far better at the event. Bad report (SUE ≤ −1 and profit down ≥ 1.5% of equity) → −1.2 pp, 40%, both periods: a weak avoid signal.

## 6. What is paper-traded

**"Growth + trend basket"**: on the last session of each month, rank liquid stocks (≥ 2m zł/day) on the G+M score, paper-buy the best 5 at the close, sell at the close of the last session of the next month. Costs per stock 0.9–2.0%. Benchmarks: WIG over the same dates, and the deposit.

**Avoid list**: the worst fifth on the same day. No new longs in those names during the month.

Ranking on 20 Nov 2026 (provisional; the first basket opens at the 30 Nov close): best LPP, Benefit, PGE, Asbis, Allegro; reserves Inter Cars, GPW, Orange, Auto Partner, Żabka. Worst fifth: Kruk, Azoty, Lubawa, Modivo, Scanway, Diagnostyka, Text, Rainbow, Develia.

## 7. Files

`lib36.py` prices, WIG proxy, costs · `fac36.py` monthly evaluator and price factors · `fund36.py` point-in-time statements · `gm36.py` the composite · `signal_now.py [date]` current ranking · `run_fund.py`, `combo36.py`, `rob36.py`, `ev36.py`, `coh.py` the tests · `output/` printed tables, monthly results (`gm_monthly.csv`), cohort table.

Run order: `run_fund.py` → `combo36.py` → `rob36.py`. Refresh: `.github/workflows/research-prices.yml` (evenings of the 25th–31st) and `.github/workflows/fundamentals.yml` (12th and 26th, 70 most liquid, income statement + balance sheet).
