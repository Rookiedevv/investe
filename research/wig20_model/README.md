# WIG20 dip model (research, Oct 2026)

Walk-forward test of whether WIG20 "dips" (falls over the next 1/3/5 sessions from the next open)
can be predicted from past prices and foreign markets. Run from the repo root:

    python research/wig20_model/walkforward.py ETFBW20TR      # proxy (Beta ETF WIG20TR, 2019-)
    python research/wig20_model/walkforward.py WIG20          # once data/prices/WIG20.csv has history

Outputs predictions.csv and scores.csv next to the scripts. The interactive page is built from
page_head.html + page_body.html with the exported data.json (see the chat session of 23 Oct 2026).

Result on the proxy (test window Oct 2022 – Oct 2026, 950 sessions): next-session AUC 0.50–0.52 (noise),
5-session AUC ≈ 0.55 but every short rule loses after 0.1% costs; after a ≥3% dip the next 5 sessions
averaged +0.65%. No usable short edge.
