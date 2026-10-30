# Round 9 (30 Oct 2026)

## A. Results drift on every pre-session report (`r9a.py`, `pre_session.py`)
**Data:** 330 first-news results or preliminary filings made before 09:00, from 23 stocks (2016–2026). Timing comes from `claude/results_calendar.csv`. A filing is skipped when an earlier release of the same quarter came within 30 sessions.

**Trade:** entry at the release-day close, hold 21 sessions.

**Comparison:** after costs, vs the WIG20 total-return ETF over the same dates.

**Excess:** the vs-ETF result minus a random 21-session hold of the same stock.

**Liquidity:** L1 = big liquid names (cost 1%); L2 = smaller names (1.5%).

| Release-day reaction vs WIG20 | Universe | n | vs ETF | Median | t | Beats ETF | <2022 / 2022+ | Excess |
|---|---|---|---|---|---|---|---|---|
| **+2% to +6% (current rule)** | L1 | 66 | **+4.3 pp** | +3.4 | 3.4 | 59% | +5.4 / +3.1 | +4.3 |
| **+3% to +6%** | L1 | 40 | **+5.5 pp** | +4.9 | 3.7 | **70%** | +7.3 / +3.8 | +5.6 |
| +3% to +6% | L1+L2 | 52 | +4.5 pp | +3.7 | 2.9 | 63% | +5.1 / +3.7 | +4.3 |
| above +6% | L1 | 18 | −0.5 pp | +1.6 | — | 56% | +2.6 / −1.6 | 0.0 |
| 0 to +2% | L1 | 65 | +0.1 pp | −0.6 | — | 45% | — | −0.2 |
| −2% to 0 | L1 | 56 | −0.7 pp | −1.6 | — | 43% | — | −0.9 |
| below −2% | L1 | 60 | +1.2 pp | −0.3 | — | 47% | — | +1.2 |

**Verdict:** the rule holds on the full set and passes the ETF bar in both periods, with the edge smaller since 2022.

**Change:** raise the lower threshold from +2% to **+3%**. The +3–6% band beats the ETF in 70% of trades (vs 59% for +2–6%), and the original 22 Oct research already showed +3–6% as the stronger band.

**Per stock:** XTB loses (−4.7 pp, n=4), consistent with the original research listing XTB among the negative names. Big contributors are Budimex, Orlen, Pepco, LPP, mBank and Synektik.

## B. Analyst recommendations (`r9b.py`, data `recs.csv`, built by `build_recs.py` from `raw/`)
**Data:** 1,248 public brokerage recommendations, 2018–Oct 2026, for 37 liquid GPW stocks. Main source: stockwatch.pl per-company pages, with biznesradar and strefainwestorow lists for 2025–26.
- Stockwatch shows the broker's **issue date**. Some brokers (BOŚ, Trigon, BDM) make reports public 5–8 days later, so entries are tested at the issue date and 1, 5 and 8 sessions after it.
- **Lag 5 or later is the realistic one.**
- DM BOŚ bulk-dated batches are excluded.
- Big-bank coverage thins after 2023: the large brokers no longer publish them.

**Trade:** hold 21 sessions. Results are after costs, vs the WIG20 total-return ETF over the same dates.

| Signal | n | lag 0 | lag 1 | **lag 5** | lag 8 | Verdict |
|---|---|---|---|---|---|---|
| Any recommendation | 1,176 | +0.5 pp, 51% | +0.6, 50% | +0.3, 49% | +0.5, 49% | — |
| Upgrade (same broker, better rating) | 215 | +1.0, 54% | +1.2, 48% | **−0.4, 47%** | −0.7, 47% | Rejected: the move happens before the public can trade |
| Downgrade | 212 | −0.5, 43% | −0.2, 46% | +0.2, 50% | +0.9, 53% | Rejected |
| Buy with ≥ 30% upside | 201 | +1.5, 60% | +1.6, 55% | +0.1, 48% | +0.8, 54% | Rejected |
| Target raised ≥ 15% | 290 | +2.2, 59% | +1.9, 57% | +1.3, 52% (t 2.2) | +0.9, 53% | Rejected (beats ETF only 52% once tradable) |
| **Target cut ≥ 15%** | 150 | −1.9, 43% | −1.6, 43% | **−1.8, 36%** (t −1.8) | −0.9, 41% | **Weak avoid signal:** the stock lags the ETF in both periods (−1.75 / −1.82). An XTB short still loses (−1.6 to −2.1% absolute), because these stocks rose overall |
| Sell/reduce | 159 | +0.1, 42% | +0.7, 48% | +1.5, 51% | +2.3, 49% | Rejected (sells don't work either) |

**Conclusion:** public Polish recommendations carry no tradable edge once they are actually public. What information there is gets priced before or on the issue date, when only the broker's clients have the report. The only use is a mild avoid filter: don't open a long in a stock for about a month after a broker cuts its target by 15% or more.
