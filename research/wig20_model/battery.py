"""Broader battery on the WIG20 proxy: rule tests with significance, regime/volatility models,
event-driven tests, and an overnight-vs-intraday decomposition. All out-of-sample where a fit is
involved (expanding window), otherwise full sample with the number of tests accounted for."""
from __future__ import annotations
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import features as F
warnings.filterwarnings("ignore")
DATA = "data"

base = sys.argv[1] if len(sys.argv) > 1 else "ETFBW20TR"
f = F.build(base)
if base == "WIG20": f = f[f.index >= "1995-01-01"]
f["gap_next"] = np.log(f["next_open"] / f["close"])          # overnight t -> t+1 open (not tradable at open)
f["t_oc1"] = f["t_oc1"]; ok = f["t_oc1"].notna() & f["r60"].notna()
f = f[ok].copy()
N = len(f)
print(f"sample {f.index.min().date()} .. {f.index.max().date()}, {N} sessions\n")

def tstat(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    return (x.mean() / (x.std(ddof=1) / np.sqrt(len(x))) if len(x) > 2 else np.nan), len(x)

# ───────── 1. Rule battery: condition -> next 1/3/5-day open->close mean; one-sided t for "down"
rules = {
 "down day": f.r1 < 0, "2 down days": f.streak <= -2, "3 down days": f.streak <= -3, "4+ down days": f.streak <= -4,
 "up day": f.r1 > 0, "3+ up days": f.streak >= 3, "5+ up days": f.streak >= 5,
 "big down day (<-1.5%)": f.r1 < -0.015, "big up day (>1.5%)": f.r1 > 0.015,
 "dip 3% from 20d high": f.dd20 <= -0.03, "dip 5% from 20d high": f.dd20 <= -0.05, "dip 10% from 60d high": f.dd60 <= -0.10,
 "at 20d high": f.dd20 > -0.002, "at 250d high": f.dd250 > -0.002, "new 20d low": f.up20 < 0.002,
 "below MA200": f.ma200 < 0, "above MA200": f.ma200 > 0, "below MA50 & above MA200": (f.ma50 < 0) & (f.ma200 > 0),
 "RSI14>70": f.rsi14 > 70, "RSI14<30": f.rsi14 < 30, "RSI3>90": f.rsi3 > 90, "RSI3<10": f.rsi3 < 10,
 "z20 > +2": f.zscore20 > 2, "z20 < -2": f.zscore20 < -2,
 "gap up >0.5% today": f.gap > 0.005, "gap down >0.5% today": f.gap < -0.005,
 "high vol (vol20>1.5%)": f.vol20 > 0.015, "low vol (vol20<0.8%)": f.vol20 < 0.008, "vol expanding (vol10/vol60>1.5)": f.volratio > 1.5,
 "volume spike (>2x)": f.volu_ratio > 2, "SPX down >1%": f.spx_r1 < -0.01, "SPX down >2%": f.spx_r1 < -0.02, "SPX up >1%": f.spx_r1 > 0.01,
 "SPX down 5d >3%": f.spx_r5 < -0.03, "NDQ down >2%": f.ndq_r1 < -0.02, "DAX down >1.5%": f.dax_r1 < -0.015,
 "VIX z>1": f.vix_z > 1, "VIX z>2": f.vix_z > 2, "VIX jump >10%": f.vix_chg1 > 0.0953, "VIX >25": f.vix > 25, "VIX <15": f.vix < 15,
 "Brent up >3%": f.brent_r1 > 0.03, "Brent down >3%": f.brent_r1 < -0.03, "PLN weak >0.5% vs EUR": f.eurpln_r1 > 0.005, "PLN strong >0.5%": f.eurpln_r1 < -0.005,
 "WIG20 lagging SPX 5d by >3%": f.spx_minus_wig_r5 > 0.03, "WIG20 ahead of SPX 5d by >3%": f.spx_minus_wig_r5 < -0.03,
 "Monday next": f.next_is_monday == 1, "Friday next": f.dow == 3, "turn of month": f.turn_of_month == 1, "expiry week": f.expiry_week == 1,
 "January": f.month == 1, "May": f.month == 5, "September": f.month == 9, "December": f.month == 12,
}
rows = []
for name, m in rules.items():
    m = m.fillna(False)
    for h in (1, 3, 5):
        col = f"t_oc{h}"; x = f.loc[m, col].dropna(); allx = f[col].dropna()
        if len(x) < 25: continue
        t, n = tstat(x)
        rows.append(dict(rule=name, h=h, n=n, mean=x.mean()*100, p_down=(x < 0).mean(), all_mean=allx.mean()*100,
                         diff=(x.mean()-allx.mean())*100, t_vs_zero=t, t_vs_all=(x.mean()-allx.mean())/(x.std(ddof=1)/np.sqrt(n))))
B = pd.DataFrame(rows)
ntests = len(B)
print(f"RULE BATTERY: {len(rules)} rules x 3 horizons = {ntests} tests; Bonferroni threshold |t| > {abs(__import__('scipy').stats.norm.ppf(0.05/2/ntests)):.2f} (two-sided 5%)")
print("Most negative (short candidates), by t vs all days:")
print(B.sort_values("t_vs_all").head(12).to_string(index=False, float_format=lambda v: f"{v:.2f}"))
print("\nMost positive (do-not-short), by t vs all days:")
print(B.sort_values("t_vs_all", ascending=False).head(8).to_string(index=False, float_format=lambda v: f"{v:.2f}"))
B.to_csv(f"research/wig20_model/battery_rules_{base}.csv", index=False)

# ───────── 2. Overnight vs intraday decomposition
print("\nOVERNIGHT vs INTRADAY (mean per session, t):")
for col, lab in (("gap_next", "close->next open (overnight)"), ("t_oc1", "next open->close (intraday)"), ("t_cc1", "close->close")):
    t, n = tstat(f[col]); print(f"  {lab:32s} {f[col].mean()*100:+.3f}%  t={t:+.2f}  P(<0)={(f[col]<0).mean():.2f}")
for y, g in f.groupby(f.index.year):
    print(f"  {y}: overnight {g.gap_next.mean()*100:+.3f}%  intraday {g.t_oc1.mean()*100:+.3f}%  (n={len(g)})")

# ───────── 3. Two-state Gaussian HMM on daily close->close returns, walk-forward (fit on past only)
def hmm_fit(x, iters=60):
    # Baum-Welch for a 2-state Gaussian HMM; returns params
    mu = np.array([x.mean()+x.std()*0.3, x.mean()-x.std()*0.3]); sd = np.array([x.std()*0.7, x.std()*1.6])
    A = np.array([[0.95, 0.05], [0.05, 0.95]]); pi = np.array([0.5, 0.5]); T = len(x)
    for _ in range(iters):
        E = np.exp(-0.5*((x[:, None]-mu)/sd)**2)/(sd*np.sqrt(2*np.pi)) + 1e-300
        al = np.zeros((T, 2)); c = np.zeros(T); al[0] = pi*E[0]; c[0] = al[0].sum(); al[0] /= c[0]
        for t in range(1, T): al[t] = (al[t-1] @ A)*E[t]; c[t] = al[t].sum(); al[t] /= c[t]
        be = np.zeros((T, 2)); be[-1] = 1
        for t in range(T-2, -1, -1): be[t] = (A @ (E[t+1]*be[t+1]))/c[t+1]
        g = al*be; g /= g.sum(1, keepdims=True)
        xi = np.zeros((2, 2))
        for t in range(T-1): v = (al[t][:, None]*A*(E[t+1]*be[t+1])[None, :]); xi += v/v.sum()
        A = xi/xi.sum(1, keepdims=True); pi = g[0]
        mu = (g*x[:, None]).sum(0)/g.sum(0); sd = np.sqrt((g*(x[:, None]-mu)**2).sum(0)/g.sum(0)) + 1e-6
    return mu, sd, A, pi

def hmm_filter(x, mu, sd, A, pi):
    E = np.exp(-0.5*((x[:, None]-mu)/sd)**2)/(sd*np.sqrt(2*np.pi)) + 1e-300
    al = pi*E[0]; al /= al.sum(); out = np.zeros((len(x), 2)); out[0] = al
    for t in range(1, len(x)): al = (al @ A)*E[t]; al /= al.sum(); out[t] = al
    return out

r = f["r1"].values; probs = np.full(N, np.nan); exp_next = np.full(N, np.nan)
for s in range(500, N, 252):
    mu, sd, A, pi = hmm_fit(r[:s], iters=40)
    bear = int(np.argmin(mu))
    fl = hmm_filter(r[:min(N, s+252)], mu, sd, A, pi)
    for t in range(s, min(N, s+252)):
        nxt = fl[t] @ A; probs[t] = nxt[bear]; exp_next[t] = nxt @ mu
f["hmm_pbear"] = probs; f["hmm_exp"] = exp_next
m = f.hmm_pbear.notna()
print(f"\nHMM (2-state, walk-forward from row 500): bear-state mean {mu[bear]*100:+.3f}%/d sd {sd[bear]*100:.2f}%, bull mean {mu[1-bear]*100:+.3f}% sd {sd[1-bear]*100:.2f}%, stay-prob {np.diag(A).round(3)}")
for thr in (0.5, 0.7, 0.9):
    mm = m & (f.hmm_pbear > thr)
    for h in (1, 3, 5):
        x = f.loc[mm, f"t_oc{h}"].dropna(); t, n = tstat(x)
        print(f"  P(bear)>{thr}: h{h} n={n} mean {x.mean()*100:+.3f}% P(down) {(x<0).mean():.2f} t={t:+.2f}")
from sklearn.metrics import roc_auc_score
y1 = (f.loc[m, "t_oc1"] < 0).astype(int); print(f"  AUC of P(bear) for next-day down: {roc_auc_score(y1, f.loc[m,'hmm_pbear']):.3f}; for 5-day down: {roc_auc_score((f.loc[m,'t_oc5']<0).astype(int)[f.loc[m,'t_oc5'].notna()], f.loc[m,'hmm_pbear'][f.loc[m,'t_oc5'].notna()]):.3f}")

# ───────── 4. GARCH(1,1)-style volatility forecast (walk-forward MLE by grid), does it carry direction?
def garch_ll(params, x):
    w, a, b = params; s2 = np.full(len(x), x.var()); ll = 0
    for t in range(1, len(x)): s2[t] = w + a*x[t-1]**2 + b*s2[t-1]
    return -0.5*np.sum(np.log(2*np.pi*s2) + x**2/s2)
from scipy.optimize import minimize
e = (f["r1"] - f["r1"].mean()).values; vol_fc = np.full(N, np.nan)
for s in range(500, N, 252):
    res = minimize(lambda p: -garch_ll(p, e[:s]), x0=[1e-6, 0.08, 0.9], bounds=[(1e-8, 1e-4), (0.01, 0.4), (0.5, 0.98)])
    w, a, b = res.x; s2 = e[:s].var()
    for t in range(1, min(N, s+252)):
        s2 = w + a*e[t-1]**2 + b*s2
        if t >= s: vol_fc[t] = np.sqrt(s2)
f["garch_vol"] = vol_fc; m = f.garch_vol.notna()
print(f"\nGARCH(1,1) walk-forward: last fit w={w:.2e} a={a:.3f} b={b:.3f}; corr(forecast vol, |next oc|)={np.corrcoef(f.loc[m,'garch_vol'], f.loc[m,'t_oc1'].abs())[0,1]:.3f}")
q = pd.qcut(f.loc[m, "garch_vol"], 4, labels=["q1 calm", "q2", "q3", "q4 stormy"])
print(f.loc[m].groupby(q)[["t_oc1", "t_oc5"]].agg(["mean", lambda x: (x<0).mean(), "count"]).rename(columns={"<lambda_0>": "P(down)"}).apply(lambda c: c*100 if c.name[1]=="mean" else c).round(3).to_string())

# ───────── 5. Event-driven: political events, bank sector shocks, utility events -> WIG20
ev = []
pol = pd.read_csv(f"{DATA}/political_events.csv", dtype=str)
for r_ in pol.itertuples(): ev.append(("political:"+r_.category, r_.date, r_.session_timing))
bank = pd.read_csv(f"{DATA}/bank_events.csv", dtype=str)
for r_ in bank[bank.category == "sector_shock"].itertuples(): ev.append(("bank_shock:"+r_.event_type, r_.date, r_.session_timing))
util = pd.read_csv(f"{DATA}/util_events.csv", dtype=str)
for r_ in util.itertuples(): ev.append(("util:"+r_.event_type+("+" if r_.sign=="1" else "-" if r_.sign=="-1" else "0"), r_.date, r_.session_timing))
sessions = f.index
def session_after(date, timing):
    d = pd.Timestamp(date); i = sessions.searchsorted(d)
    if i >= len(sessions): return None
    if sessions[i] == d and timing in ("before", "pre_open", "non_trading_day", "during", "intraday", "unknown", "", None) and timing not in ("after", "after_close"):
        return i   # reaction on the event day itself
    return i if sessions[i] > d else i + 1   # after-close or weekend -> next session
E = pd.DataFrame(ev, columns=["kind", "date", "timing"]); E["i"] = [session_after(d, t) for d, t in zip(E.date, E.timing)]
E = E.dropna(subset=["i"]); E["i"] = E.i.astype(int); E = E[E.i < N-6]
E["group"] = E.kind.str.split(":").str[0]
# reaction day (day 0, close->close), then the following 1/3/5 sessions open->close (tradable after seeing day 0)
cc = f["t_cc1"].values;
for grp, g in E.groupby("group"):
    idx = g.i.values - 1  # row whose t_cc1 is the reaction day
    idx = idx[idx >= 0]
    d0 = cc[idx]; d0 = d0[~np.isnan(d0)]
    print(f"\nEVENTS {grp}: n={len(idx)} | reaction day close->close mean {d0.mean()*100:+.2f}% sd {d0.std()*100:.2f}% P(down) {(d0<0).mean():.2f} | share of |move|>1.5%: {(np.abs(d0)>0.015).mean():.2f} (all days {(f.t_cc1.abs()>0.015).mean():.2f})")
    for h in (1, 3, 5):
        x = f[f"t_oc{h}"].values[g.i.values]; x = x[~np.isnan(x)]; t, n = tstat(x)
        print(f"   after day 0, next {h}: n={n} mean {x.mean()*100:+.2f}% P(down) {(x<0).mean():.2f} t={t:+.2f}")
    # conditional on the reaction direction: did a negative reaction continue?
    neg = g.i.values[cc[g.i.values-1] < -0.01]
    if len(neg) >= 8:
        for h in (1, 3, 5):
            x = f[f"t_oc{h}"].values[neg]; x = x[~np.isnan(x)]; t, n = tstat(x)
            print(f"   reaction < -1% -> next {h}: n={n} mean {x.mean()*100:+.2f}% P(down) {(x<0).mean():.2f} t={t:+.2f}")
print("\nEvent kinds with n>=10 (reaction day mean %, next-3 mean %):")
for kind, g in E.groupby("kind"):
    if len(g) < 10: continue
    d0 = cc[g.i.values-1]; x3 = f["t_oc3"].values[g.i.values]
    print(f"  {kind:40s} n={len(g):3d} day0 {np.nanmean(d0)*100:+.2f}%  next3 {np.nanmean(x3)*100:+.2f}% P(down3) {(x3[~np.isnan(x3)]<0).mean():.2f}")
f.to_pickle(f"research/wig20_model/battery_frame_{base}.pkl")
