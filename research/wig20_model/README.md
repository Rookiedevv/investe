# WIG20 dip model (research, Oct 2026)

Walk-forward test of whether WIG20 "dips" (falls over the next 1/3/5 sessions from the next open)
can be predicted from past prices and foreign markets. Run from the repo root:

    python research/wig20_model/walkforward.py ETFBW20TR      # proxy (Beta ETF WIG20TR, 2019-)
    python research/wig20_model/walkforward.py WIG20          # once data/prices/WIG20.csv has history

Outputs predictions.csv and scores.csv next to the scripts. The interactive page is built from
page_head.html + page_body.html with the exported data.json (see the chat session of 23 Oct 2026).

## WIG20 short-term dips (short FW20) — 23 Oct 2026
Data: Beta ETF WIG20TR (Yahoo, Jan 2019 – 22 Oct 2026) as WIG20 proxy (Yahoo no longer serves WIG20 history; Stooq blocks automated downloads); S&P 500, Nasdaq, DAX, VIX, Brent, EUR/PLN, USD/PLN from Yahoo. Decision each evening after the US close, entry at the next Warsaw open, cost 0.10% per round trip (FW20). Models: logistic regression and gradient boosting on ~55 features (WIG20 returns/volatility/range/gap/drawdowns/MAs/RSI/streaks/volume, foreign 1–20-day moves, VIX, calendar), refitted every 63 sessions on an expanding window, no look-ahead. Test window Oct 2022 – Oct 2026 (950 sessions). Scripts: investe repo, research/wig20_model/; interactive page "WIG20 Dip Model".

| Hypothesis | Verdict | Evidence |
|---|---|---|
| Next-session direction (open→close) can be predicted | Rejected | Best AUC 0.52 (ensemble 0.519, base rate 0.48); accuracy 49–51% vs 50.4% base. Shorting when P(down) > 0.50/0.55/0.60: 579/368/195 trades, −0.04% / −0.02% / +0.03% per trade after costs, win rate 48–53%. |
| 3- and 5-session direction | Faint signal, not tradable | AUC 0.525 (3d, logistic), 0.547 (5d, ensemble). But over 5 sessions WIG20 fell only 42% of the time, and every short rule lost −0.35% to −0.47% per trade (win rate 44–45%). |
| Foreign markets add information | Marginally (5-day) | All-inputs models beat WIG20-only models by ~0.01–0.02 AUC at 3–5 days; at 1 day no difference. After an S&P 500 fall ≥1% the next WIG20 session averaged +0.09% (P(down) 0.45): the news is in the overnight gap, not in the next day's open→close. |
| Dips continue ("take advantage of dips however long they take") | Rejected — dips revert | ≥3% below the 20-day high (318 days): next session −0.00%, next 5 sessions +0.65% (P(down) 0.41). Open→close returns have negative autocorrelation (−0.12), i.e. a down day is more often followed by an up day. Structural drift: next-session open→close mean −0.02%, overnight gap +0.13%/day — the index gains overnight, not during the session. |

Implication: with daily data alone there is no way to call WIG20 dips in advance; the only robust facts are that WIG20 drifted up (gaps) over 2020–26 and that falls reverted. A short-FW20 approach would need an event-driven trigger (an actual announcement before the open), not a price pattern. Real WIG20 bars are now collected daily by the investe pipeline (data/prices/); a Stooq WIG20 file would allow re-running from 1994 and a check of whether 2008/2011/2020-type regimes behave differently.

## Second round (battery.py, 23 Oct 2026)
| Approach | Result for a short |
|---|---|
| Rule battery: 55 conditions × 3 horizons (165 tests) | Nothing survives Bonferroni. Best candidate: 4 consecutive down days → next 3 sessions −0.9% (46 non-overlapping trades, 61% down, 7/8 years negative, t −2.0); absent in PKO/PEO/PGE/CAR. "VIX<15" is 2019–early 2020 only. |
| 2-state HMM regime (walk-forward) | Stormy regime is a buy: next 5 sessions +1.0 to +1.5% (t>3); direction AUC 0.50. |
| GARCH(1,1) (walk-forward) | Predicts magnitude (corr 0.23 with next absolute move), not sign. |
| Events: 134 political, 56 bank shocks, 98 utility, mapped to the correct session | No follow-through after the reaction day (−0.1% to +0.4%); elections/government −0.5% over 3 days on 12/21 cases. |
| Overnight vs intraday | +0.14%/session overnight, −0.10% intraday, every year; not tradable, but a short should be opened at the open. |

## Full history (WIG20 Stooq seed 1995–2026, 23 Oct 2026)
Walk-forward (train from 1995, refit every 126 sessions): 6,459 OOS sessions 2001–2026, AUC 0.51–0.52 at 1/3/5 days for every model — the 5-day signal on the ETF proxy was noise. Rule battery (165 tests): only September passes at day level; by month −2.0% per September, down 19/32 years (t −1.7), negative 2015–2024, positive 2025–26. 4-down-days rule from the proxy disappears (next session up 63%); 5 down days (n=94): −0.5 to −0.8% over 3–5 sessions, t −1.8, fails correction. HMM stormy regime still a buy (+0.24–0.32% over 5 sessions, t ~3). GARCH magnitude only (corr 0.30). Events: no follow-through. Overnight effect only +0.04%/session over the full history. Calendar longs robust: turn of month +0.5%, December +0.7% over 5 sessions (t 5.1 / 4.7). FW20 tracks WIG20 (corr 0.977, basis +0.04%, tick 0.024%).
Verdict unchanged: no reliable short signal from prices, regimes, volatility, calendar or the event files. Only a modest "avoid/short in September" seasonal is worth watching.

## Round 3 (round3.py, 23 Oct 2026) — same-day decisions, futures, holidays, monthly momentum
- 9:01 decision with the gap known: gaps continue slightly (gap down >0.5% → open→close −0.11%, t −2.9; gap up >1% → +0.18%; gap much weaker than SPX implied → −0.12%, t −3.0) but after a gap down the session still rose 54% of the time. Same-day walk-forward model (lagged features + gap, basis, OI, holidays): AUC 0.52, acc 51.7%, −0.05 to −0.10% per trade after 0.1% cost; AUC by era 0.545 / 0.496 / 0.513.
- FW20 basis / open interest (1998–2026): corr with next 1–5 days −0.04..+0.01; cheap futures (basis z<−1.5) → +0.29% over 5d (t 2.3), a long signal.
- Holidays: pre/post ±0.08%, t≈1. Monthly momentum: 12m lookback hit 56% = base rate (54.5% months up); after negative 12m, next month down 51%.
- Note: the models beat a coin toss statistically (52% on 6,459 days, 3 s.e.) but not costs; a usable short needs ~55%+ or the big days. Untested avenues: intraday FW20 (5-min from Stooq) and a pre-open news feed.
