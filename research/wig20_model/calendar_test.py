"""Scheduled Polish decision dates vs WIG20: anticipation drift, reaction, aftermath, volatility.
Dates known in advance: NBP rate decisions (2019-26), CJEU/Supreme Court CHF rulings and AG opinions,
KNF dividend positions, bank results releases, elections (first session after), futures expiry /
index rebalancing (3rd Friday Mar/Jun/Sep/Dec)."""
from __future__ import annotations
import sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/wig20_model")
import features as F
DATA = "data"

w = F.load("WIG20"); w = w[w.index >= "1995-01-01"]
c = w["close"]; o = w["open"]; r = np.log(c).diff(); sessions = w.index
spx = F.load("SPX")["close"].reindex(sessions, method="ffill"); rs = np.log(spx).diff()
dax = F.load("DAX")["close"].reindex(sessions, method="ffill"); rd = np.log(dax).diff()
r_ex = r - 0.5*(rs + rd.fillna(0))            # WIG20 beyond world markets (rough: beta 0.5 to the average)

# bank basket 2016-10 .. (equal-weight 9 banks), excess over WIG20
banks = []
for t in ("PKO", "PEO", "EBP", "MBK", "ING", "MIL", "ALR", "BHW", "BNP"):
    try: banks.append(np.log(F.load(t)["adj_close"]).diff().rename(t))
    except FileNotFoundError: pass
rb = pd.concat(banks, axis=1).mean(axis=1).reindex(sessions)
rb_ex = rb - r

def session_on_or_after(d, timing):
    d = pd.Timestamp(d); i = sessions.searchsorted(d)
    if i >= len(sessions): return None
    if sessions[i] == d and timing not in ("after", "after_close"): return i
    return i if sessions[i] > d else i + 1

def profile(name, idxs, series=r, pre=(-5, -1), post=(1, 5), show=True):
    idxs = sorted({i for i in idxs if i is not None and 25 <= i < len(sessions) - 25})
    if len(idxs) < 5: return None
    M = np.array([[series.iloc[i + k] for k in range(-10, 11)] for i in idxs])
    M = np.nan_to_num(M)
    pre_r = M[:, 10 + pre[0]:10 + pre[1] + 1].sum(1); day = M[:, 10]; post_r = M[:, 10 + post[0]:10 + post[1] + 1].sum(1)
    absday = np.abs(M[:, 10]); typ = series.abs().rolling(60).mean().reindex(sessions).iloc[idxs].values
    t = lambda x: x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))
    out = dict(name=name, n=len(idxs), pre=pre_r.mean()*100, pre_t=t(pre_r), pre_down=(pre_r < 0).mean(),
               day=day.mean()*100, day_t=t(day), day_down=(day < 0).mean(), absratio=np.nanmean(absday/typ),
               post=post_r.mean()*100, post_t=t(post_r), post_down=(post_r < 0).mean())
    if show:
        print(f"{name:46s} n={out['n']:3d} | pre -5..-1 {out['pre']:+.2f}% (t{out['pre_t']:+.1f}, P↓{out['pre_down']:.2f}) | day {out['day']:+.2f}% (t{out['day_t']:+.1f}, P↓{out['day_down']:.2f}, |move| {out['absratio']:.2f}x) | post +1..+5 {out['post']:+.2f}% (t{out['post_t']:+.1f}, P↓{out['post_down']:.2f})")
    return out

b = pd.read_csv(f"{DATA}/bank_events.csv", dtype=str).fillna("")
cal = {}
cal["NBP rate decision (2019-26)"] = [session_on_or_after(d, t) for d, t in zip(b[b.event_type == "nbp_rate_decision"].date, b[b.event_type == "nbp_rate_decision"].session_timing)]
chf = b[b.event_type.isin(["chf_ruling", "chf_ag_opinion"])]
cal["CJEU / Supreme Court CHF ruling"] = [session_on_or_after(d, t) for d, t in zip(chf.date, chf.session_timing)]
knf = b[b.event_type == "knf_dividend_policy"]
cal["KNF dividend position"] = [session_on_or_after(d, t) for d, t in zip(knf.date, knf.session_timing)]
res = b[b.category == "bank_results"]
cal["Bank results release (2019-26)"] = [session_on_or_after(d, t) for d, t in zip(res.date, res.session_timing)]
elections = {"parliamentary": ["2005-09-25", "2007-10-21", "2011-10-09", "2015-10-25", "2019-10-13", "2023-10-15"],
             "presidential (each round)": ["2005-10-09", "2005-10-23", "2010-06-20", "2010-07-04", "2015-05-10", "2015-05-24", "2020-06-28", "2020-07-12", "2025-05-18", "2025-06-01"],
             "EU / local": ["2004-06-13", "2009-06-07", "2014-05-25", "2019-05-26", "2024-06-09", "2014-11-16", "2018-10-21", "2024-04-07"]}
for k, ds in elections.items():
    cal[f"Election {k} (first session after)"] = [session_on_or_after(d, "non_trading_day") for d in ds]
cal["Election: any (first session after)"] = sum((cal[f"Election {k} (first session after)"] for k in elections), [])
# futures expiry: 3rd Friday of Mar/Jun/Sep/Dec, 1998-2026 (also the index rebalancing day)
exp = []
for y in range(1998, 2027):
    for m in (3, 6, 9, 12):
        d = pd.Timestamp(year=y, month=m, day=15); d = d + pd.Timedelta(days=(4 - d.weekday()) % 7)
        if d <= sessions[-1]: exp.append(session_on_or_after(d, "during"))
cal["Futures expiry / index rebalancing day"] = exp
cal["Session after expiry (new index weights)"] = [i + 1 for i in exp if i is not None]

print("=== WIG20 around scheduled dates: pre-drift (5 sessions before), event day, 5 sessions after ===")
rows = []
for k, v in cal.items():
    o_ = profile(k, v)
    if o_: rows.append(o_)
print("\n=== Same, WIG20 beyond world markets (minus 0.5 x average of S&P/DAX) ===")
for k in ("NBP rate decision (2019-26)", "CJEU / Supreme Court CHF ruling", "KNF dividend position", "Election: any (first session after)", "Futures expiry / index rebalancing day"):
    profile(k, cal[k], series=r_ex)
print("\n=== Bank basket beyond WIG20 (2016-10 onward) ===")
for k in ("NBP rate decision (2019-26)", "CJEU / Supreme Court CHF ruling", "KNF dividend position", "Bank results release (2019-26)"):
    profile(k, cal[k], series=rb_ex)

# NBP: split by outcome known from the file text (hike / cut / hold) and by direction of surprise is not in the file; show hike vs cut vs hold
print("\n=== NBP decisions by outcome (from the event text) ===")
nbp = b[b.event_type == "nbp_rate_decision"].copy()
nbp["kind"] = np.where(nbp.description.str.contains("hike|raise|podw|increase|\\+", case=False), "hike",
                       np.where(nbp.description.str.contains("cut|lower|obni|reduc|-", case=False), "cut", "hold"))
for kind, g in nbp.groupby("kind"):
    profile(f"NBP {kind}", [session_on_or_after(d, t) for d, t in zip(g.date, g.session_timing)])
pd.DataFrame(rows).to_csv("research/wig20_model/calendar_results.csv", index=False)
