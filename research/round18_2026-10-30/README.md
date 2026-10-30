# Round 18 (30 Oct 2026): futures basis, ETF seasonality, panic-signal overlap, monthly reversal, serial drifters

Benchmark everywhere: WIG20 TR ETF over the same dates (WIG20 + 3.5%/yr before Feb 2019), minus 0.78% round trip; stock legs at eMakler costs.
Insider trades (`claude/insider_trades.csv`) were already tested in the results-drift round (buys −0.1 pp vs WIG, n=77) and were not re-run.

## A. WIG20 futures basis (`r18a.py`, FW20 front contract vs cash, 2011–26)
Deviation of the basis from its 60-session median, 250-session z-score. Correlation with the next 21 sessions −0.035. z ≤ −1.5 (futures cheap): +1.2% vs −0.0 unconditional, 63%, n=46; z ≥ +1.5 (futures rich): +1.1%, 59%, n=47 — both sides "positive", i.e. noise. **Rejected.**

## B. ETF seasonality 2011–26 (`r18a.py`)
Mean month: Jan +1.6, Apr +2.2, Jul +1.5, Oct +2.2, Nov +1.6, Dec +1.6; Mar −0.8, Sep −1.8, Aug −0.4. Nov–Apr +1.0%/month vs May–Oct +0.3%, but the split is 2015–26 only (2011–14: −0.1 vs +0.1), and win rates are 51–52% either way. A 16-year sample cannot carry a calendar rule. **Not a rule;** at most a reason not to add long ETF exposure in Aug–Sep.

## C. Panic-signal overlap (`r18a.py`, SII survey weeks, entry next session, 21 sessions)
| Signal | n | 4w | win |
|---|---|---|---|
| SII bull−bear z ≤ −1.5 | 35 | +2.6% | 66% |
| WIG20 ≥ 8% below its 21-day high | 27 | +2.0% | 56% |
| **both** | 13 | **+5.3%** | 69% |
| SII only | 28 | +2.2% | 64% |
| drawdown only | 18 | +1.3% | 56% |

Both at once (a real sell-off that retail actually fears) is the strongest ETF-timing signal found so far, but 13 cases in 15 years. Kept as a timing tilt for the ETF leg, same status as round 17.

## D. Cross-sectional monthly reversal / continuation among the 42 liquid names (`r18b.py`, month-end rebalance, hold 21, 142 months 2015–26)
| Portfolio | vs ETF per month | beats ETF | t |
|---|---|---|---|
| bottom 5 past-month laggards | +0.5 pp | 47% | 1.0 (2019+: −0.3) |
| bottom 5 past-week laggards | +0.6 pp | 46% | 1.0 |
| bottom 5 past-quarter laggards | −0.2 pp | 47% | −0.4 |
| names ≥ 15 pp behind WIG20 | +1.2 pp | 42% | 0.8 (2019+: −1.0) |
| top 5 past-month leaders | +1.8 pp | 53% | 3.0 (both eras ≈ +1.7–2.0) |
| names ≥ 10 pp ahead | +1.9 pp | 53% | 2.5 |

Reversal: nothing, and negative since 2019. One-month continuation looks like the 12-1 momentum result from round 4 (+0.9 pp, 53%) — positive mean, coin-flip hit rate, built on today's liquid names (survivorship). **Rejected as a rule**; momentum tilt noted again.

## E. Serial drifters — history conditioning of the live drift rule (`r18c.py`, 32 signals 2014–26, L1 ex banks ex XTB)
All: +6.3 pp vs ETF, 75%, t 3.9. Previous reaction > 0: +6.1 pp / 77%; ≤ 0: +6.2 pp / 72%. Previous post-report drift up: +6.6 / 76%; down: +5.6 / 71%. ≥ 3 of last 4 drifts positive: +8.3 / 90% (n=10); ≤ 1 of 4: +7.0 / 50% (n=8). **No conditioning changes the rule**; the drift does not depend on the company's recent report history, which is reassuring for the live check (nothing to add). Per name: BDX +12.9 pp (6), PCO +9.8 (5), CPS +5.1 (4), PZU +4.5 (4).
