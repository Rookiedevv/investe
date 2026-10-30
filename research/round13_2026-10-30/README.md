# Round 13 (30 Oct 2026): bank read-through re-audit; web-data rounds pending approval

## A. Bank early-reporter read-through vs the WIG20 TR ETF (`r13a.py`, bank calendar `round12_2026-10-30/r12e_cal.py`)
Live paper rule (trades 4–8 in `claude/paper_trades_log.csv`): early reporter's results-day move minus the late reporters' average same-day move ≥ +1.5 pp → buy the late reporters at the reaction-day close; exit on the first day the stock falls more than 1.5× its normal daily move, max 20 sessions. The original note (research_log.md) already said "promising, unproven": +4.7% per trade over 6 seasons, but late banks did not beat the sector and the best seasons were market rallies.

Re-run on all 197 bank filings 2021–26 (22 reporting seasons; Q4 prelims and annual reports treated as one season, first filing per bank; reaction day = filing day for pre-session filings, next day for after-session ones; late reporters = banks reporting ≥ 2 sessions after the early one; cost 1%).

| Signal S (early reporter vs late reporters, same day) | Trades | Hold to own report (≤ 20) | Trailing exit 1.5× noise | Fixed 20 sessions |
|---|---|---|---|---|
| **S ≥ +1.5 pp (the buy signal)** | 39 (8 seasons) | **−0.0 pp vs ETF, 56% beat** | −0.1 pp, 51% | +0.9 pp, 59% (t 0.7) |
| S ≥ +1.0 | 53 | +0.6 pp, 58% | +0.5 pp, 55% | +1.7 pp, 62% (t 1.6) |
| S ≥ +2.5 | 33 | −0.1 pp | +0.1 pp | +1.4 pp, 61% |
| S ≤ −1.5 (stay out) | 24 | −0.9 pp, 33% | −0.8 pp, 33% | −0.6 pp, 33% |
| S within ±1.5 | 96 | +0.2 pp | +0.1 pp | −0.3 pp |
| S ≥ +1.5, tilt names MBK ING PEO PKO | 23 | −0.4 pp | −0.3 pp | +0.3 pp |

Correlation between S and the late reporters' result vs the ETF: 0.13. Season by season the buy signal worked in 2021 (three seasons, +3.5 to +4.1 pp) and failed or did nothing in most seasons since (Oct 2022 −2.6, Feb 2022 −6.3 hold-to-report, Oct 2023 −0.9, Feb 2026 −2.4, Apr 2026 −0.5).

**Verdict:** the read-through buy side does not beat the ETF over 2021–26 (0 to +1 pp, 8 signal seasons). Its gains were the bank sector moving with the market. The "stay out after a bad early report" side is weakly supported (late reporters lag the ETF by ~0.9 pp, beating it in a third of cases) but not worth a short. Keep the open paper trades to their exit, then move the rule from "paper-trade lead" to "weak / regime", and don't add it to the app's rule set. Note the clustering of seasons changes the numbers by ±1 pp, which is itself a sign there is little there.

## C. WIG20 index reversal (`r13b.py`, WIG20 2011–26, cost 0.78%)
Buying the index after a bad day or week does nothing (≤ −3% day → +1.3% over 21 sessions, 62%, t 0.8, vs −0.4% unconditional; 5-day ≤ −5% → +0.5%). The only mildly positive cell is a monthly drawdown: **WIG20 down ≥ 10% over 21 sessions → next 21 sessions +4.0% net, 73% wins, n=15, t 1.5** (2019+: +4.6%). Fifteen cases in 15 years; weak lead, not a rule. After strong months (+10%) there is no continuation and no reversal.

## B. Pending (need web pages the session could not open — approval requests timed out)
- Tender offers (wezwania) 2018–26: buy at the announcement-day close, hold to settlement; spread, raise frequency, failure losses; vs deposit and vs ETF.
- KNF net short-position register: do new disclosed shorts (≥ 0.5%) predict underperformance over the next month?
