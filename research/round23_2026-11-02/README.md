# Round 23 (2 Nov 2026): Poland sovereign rating actions (Fitch / Moody's / S&P)

**Hypothesis.** Rating changes are released on Friday evenings, after the Warsaw close, so Monday is the first session to trade on them. Two trades tested: an FW20 short for one day after a negative action (outlook cut or downgrade), and a one-month long after a positive action.

**Verdict: rejected.** Negative actions don't push the market down on Monday, and nothing follows over the next month.

## Data
16 rating or outlook changes, 2007–2026 (`r23a_events.csv`), from fxempire's rating history, theglobaleconomy and news reports of the 2025–26 actions: 7 negative, 9 positive. Prices are WIG20 and FW20 from the Stooq seed files (going back to 1991 and 1998), a 9-bank equal-weight basket (2016+) and EUR/PLN. Scheduled affirmations were not used, because exact dates would have needed page fetches that weren't approved.

## Results (first session after the announcement)
| | n | FW20 overnight gap | FW20 open→close | WIG20 day | banks day | EUR/PLN day | WIG20 +21 sessions |
|---|---|---|---|---|---|---|---|
| negative actions | 7 | +0.36% (negative in 1 of 7) | +0.52% | +0.96% | +1.96% | −0.64% (zloty firmer) | +1.95% |
| positive actions | 9 | +0.09% | +0.15% | +0.21% | +0.82% | −0.22% | +0.00% |
| all sessions since 2007 | | mean abs. gap 0.47% | −0.03% | SD 1.45% | | | +0.31% |

- Only one negative action hurt: the S&P downgrade of 15 Jan 2016, the first-ever cut and a real surprise. That Monday FW20 gapped −1.2% and fell another −2.4% open→close, WIG20 −3.2%. Every other cut or outlook cut, including Moody's cut to A3 on 18 Sep 2026, was followed by a flat-to-up Monday: the move is expected and priced in during the run-up (WIG20 −2.2% over the 5 sessions before negative actions).
- FW20 short after a negative action: −0.5% average open→close, 6 of 7 losers. Rejected.
- The one-month moves (+1.95% after negative actions) come from 2008 and 2016 crisis rebounds, with n=7. Not a rule.

Upcoming: S&P's scheduled review of Poland is on Friday 6 Nov 2026. Based on this round there is nothing to trade on it.
