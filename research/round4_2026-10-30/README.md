# New hypotheses, round 4 (tested 30 Oct 2026)

**Data:** Yahoo daily prices from this repo (`research/prices/`, `data/prices/`), 2011–29 Oct 2026, adjusted for dividends.
- **Universe:** 42 liquid names (≥ ~3m zł a day). Yahoo volumes are unreliable in level, so the universe is hand-picked from WIG20 / mWIG40 (`L1`, `L2` in `lib.py`).
- **Benchmark:** WIG20.
- **Costs:** 1.0% round trip for big caps, 1.5% for smaller names. XTB shorts pay about 0.8% plus swap.
- **Trades:** entry at the signal-day close. No overlapping trades in the same stock.
- **Baseline:** a random 21-session hold in these stocks makes +0.9% net. The stocks rose over the period, so any rule has to beat that, not zero.

**Scripts:** `h1.py` pre-results run-up (calendar in `cal.py`), `h2.py` dividends, `h3.py` volume spikes and 52-week high/low, `h4.py` 52-week-high robustness, `h5.py` cross-sectional momentum. Run them from the `research/` folder.

## Summary
| Hypothesis | n | Net | vs WIG20 | Wins | t | <2019 / 2019+ | Verdict |
|---|---|---|---|---|---|---|---|
| **New 52-week high on ≥ 2× normal volume**, buy at close, hold 21 | 514 | **+3.0%** (median +1.5) | +3.5 pp | 57% | 4.9 | +4.5 / +2.6 | **Lead** |
| same, ≥ 3× volume | 331 | +3.4% | +4.1 pp | 57% | 4.1 | +5.2 / +2.9 | |
| same, ≥ 2× volume, hold 42 | 508 | +5.2% | +5.2 pp | 56% | 5.7 | +6.4 / +5.0 | |
| Momentum: top 20% by 12-1 month return, monthly rebalance | 132 months | +1.8%/month | +0.9 pp/month | 64% of months | 2.0 vs WIG20 | +1.6 / +1.9 | Weak lead (beats WIG20 in only 53% of months; 2015, 2018 and 2022 negative) |
| Pre-results run-up (buy 5/10/21 sessions before a results date, sell the day before) | 943–1,192 | −0.7% to −0.1% | — | 39–46% | — | — | Rejected: worse than random holds |
| Dividend run-up (21 sessions before ex-date, sell cum) | 73–146 | +0.1% to +3.6% | — | 47–55% | ≤ 2.0 | — | Rejected |
| Buy at ex-dividend close, 5 or 21 sessions | 59–146 | −1.1% to 0.0% | — | 38–47% | — | — | Rejected |
| XTB short after ex-dividend | 146 | −1.4% | — | 42% | — | — | Rejected |
| Volume ≥ 3× on a quiet day / up day / down day, buy | 608–1,972 | +1.2% to +3.2% | — | 50–53% | — | — | Mostly baseline. Not adopted |
| Volume spikes or new 52-week lows as XTB shorts | 403–1,972 | −2.1% to −5.5% | — | 37–45% | — | — | Rejected |
| Shorting momentum losers / last month's winners (XTB) | 132 months | −3.1% / −4.2%/month | — | — | — | — | Rejected: losers don't fall enough, and winners keep going |

## Lead: 52-week-high breakout on volume
**Rule:** a liquid stock closes at a new 52-week high for the first time (yesterday it was below the previous 252-session high), and that day's volume is at least 2× its 60-session median. Buy at that close and sell after 21 sessions.

**Checks:**
- Same stock, random month: +1.9 pp better (t 3.2), so the result isn't just picking stocks that rose.
- Averaged per calendar month (116 months): +2.7% (t 2.9).
- 10 of 12 years positive.
- Works with WIG20 above or below its 200-day average: +2.9% / +3.3%.
- Trimmed mean +2.1%.
- Worst trade −39%, best +139% (Polimex).
- Big caps only: +2.5% (n=353).
- About 40 signals a year.

**Caveats:**
- **Survivorship:** the universe is today's liquid names, which favours stocks that went on to do well.
- Yahoo volume undercounts some names; the ratio to the stock's own median still works.
- Needs paper trading before it counts.

**Status:** paper-trade lead.
