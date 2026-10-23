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
