"""Round 3: same-day (9:01) decisions, futures basis/open interest, holidays, monthly momentum,
and a walk-forward model on the enlarged feature set. Real WIG20 1995-2026."""
from __future__ import annotations
import sys, warnings
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
sys.path.insert(0, "research/wig20_model")
import features as F
warnings.filterwarnings("ignore")

f = F.build("WIG20"); f = f[f.index >= "1995-01-01"].copy()
w = F.load("WIG20"); fw = F.load("FW20")
def tst(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    return x.mean()/(x.std(ddof=1)/np.sqrt(len(x))), len(x)

# ───────── A. Same-day information at the open (decision at 9:01, trade open->close of the SAME day)
# Row t: gap_t = open_t / close_{t-1}; spx_{t-1} known; target oc_t = close_t/open_t.
f["gap_t"] = f["gap"]; f["oc_t"] = f["oc"]
f["spx_prev"] = f["spx_r1"].shift(1); f["dax_prev"] = f["dax_r1"].shift(1); f["vixchg_prev"] = f["vix_chg1"].shift(1)
f["r1_prev"] = f["r1"].shift(1); f["ma200_prev"] = f["ma200"].shift(1); f["streak_prev"] = f["streak"].shift(1)
d = f.dropna(subset=["gap_t", "oc_t", "spx_prev", "r1_prev"]).copy()
print(f"A. SAME-DAY: {len(d)} sessions {d.index.min().date()}..{d.index.max().date()}")
print(f"   corr(gap_t, oc_t) = {np.corrcoef(d.gap_t, d.oc_t)[0,1]:+.3f};  corr(spx_prev, gap_t) = {np.corrcoef(d.spx_prev, d.gap_t)[0,1]:+.3f};  corr(spx_prev, oc_t) = {np.corrcoef(d.spx_prev, d.oc_t)[0,1]:+.3f}")
# Under-reaction: residual of gap on SPX (fit walk-forward-free: simple full-sample beta is descriptive only)
beta = np.polyfit(d.spx_prev, d.gap_t, 1)[0]; d["gap_resid"] = d.gap_t - beta*d.spx_prev
print(f"   gap beta to SPX_prev = {beta:.2f}; corr(gap residual, oc_t) = {np.corrcoef(d.gap_resid, d.oc_t)[0,1]:+.3f}")
conds = {
 "gap down >0.5%": d.gap_t < -0.005, "gap down >1%": d.gap_t < -0.01, "gap up >0.5%": d.gap_t > 0.005, "gap up >1%": d.gap_t > 0.01,
 "SPX fell >1%, gap > -0.3% (under-reaction)": (d.spx_prev < -0.01) & (d.gap_t > -0.003),
 "SPX fell >1%, gap < -1% (over-reaction?)": (d.spx_prev < -0.01) & (d.gap_t < -0.01),
 "SPX rose >1%, gap < +0.3%": (d.spx_prev > 0.01) & (d.gap_t < 0.003),
 "SPX rose >1%, gap > +1%": (d.spx_prev > 0.01) & (d.gap_t > 0.01),
 "gap down & yesterday down": (d.gap_t < -0.003) & (d.r1_prev < 0), "gap up & yesterday up": (d.gap_t > 0.003) & (d.r1_prev > 0),
 "gap down >0.5% below MA200": (d.gap_t < -0.005) & (d.ma200_prev < 0), "gap down >0.5% above MA200": (d.gap_t < -0.005) & (d.ma200_prev > 0),
 "gap down >0.5% after 2+ down days": (d.gap_t < -0.005) & (d.streak_prev <= -2), "gap down >0.5% after up day": (d.gap_t < -0.005) & (d.r1_prev > 0),
 "gap residual < -0.5% (gap much weaker than SPX implied)": d.gap_resid < -0.005, "gap residual > +0.5%": d.gap_resid > 0.005,
}
allm = d.oc_t.mean()*100
for k, m in conds.items():
    x = d.loc[m, "oc_t"]; t, n = tst(x)
    byd = d.loc[m].groupby((d.loc[m].index.year//8)*8).oc_t.mean()*100
    print(f"   {k:52s} n={n:4d} open->close {x.mean()*100:+.3f}% (all {allm:+.3f}) P(down) {(x<0).mean():.2f} t={t:+.2f} | " + " ".join(f"{y}:{v:+.2f}" for y, v in byd.items()))

# ───────── B. Futures basis and open interest
fwj = fw.join(w, lsuffix="_f", rsuffix="_i", how="inner")
fwj["basis"] = fwj.close_f/fwj.close_i - 1
# de-seasonalise the basis: subtract its 60-day rolling mean (dividend/expiry cycle), z-score
fwj["basis_z"] = (fwj.basis - fwj.basis.rolling(60).mean())/fwj.basis.rolling(60).std()
fwj["basis_chg"] = fwj.basis.diff()
lop = pd.read_csv("data/prices/seed/FW20.csv")
lop["date"] = pd.to_datetime(lop["Data"]); lop = lop.set_index("date")["LOP"]
fwj["oi"] = lop.reindex(fwj.index); fwj["oi_chg5"] = np.log(fwj.oi).diff(5); fwj["oi_z"] = (fwj.oi - fwj.oi.rolling(120).mean())/fwj.oi.rolling(120).std()
fwj["fvol_z"] = (fwj.volume_f - fwj.volume_f.rolling(60).mean())/fwj.volume_f.rolling(60).std()
g = f.join(fwj[["basis", "basis_z", "basis_chg", "oi_chg5", "oi_z", "fvol_z"]], how="left")
gb = g.dropna(subset=["basis_z", "t_oc1"])
print(f"\nB. FUTURES BASIS / OPEN INTEREST: {len(gb)} sessions from {gb.index.min().date()}; basis mean {gb.basis.mean()*100:+.2f}% sd {gb.basis.std()*100:.2f}%")
for k, m in {"basis z > +1.5 (futures rich)": gb.basis_z > 1.5, "basis z < -1.5 (futures cheap)": gb.basis_z < -1.5,
             "basis fell >0.5pp today": gb.basis_chg < -0.005, "basis rose >0.5pp today": gb.basis_chg > 0.005,
             "OI up >10% in 5d": gb.oi_chg5 > 0.095, "OI down >10% in 5d": gb.oi_chg5 < -0.105,
             "OI z > 1.5": gb.oi_z > 1.5, "OI z < -1.5": gb.oi_z < -1.5, "futures volume z > 2": gb.fvol_z > 2,
             "OI up >10% & price down 5d": (gb.oi_chg5 > 0.095) & (gb.r5 < 0), "OI up >10% & price up 5d": (gb.oi_chg5 > 0.095) & (gb.r5 > 0)}.items():
    for h in (1, 5):
        x = gb.loc[m, f"t_oc{h}"].dropna(); t, n = tst(x)
        byd = gb.loc[m].groupby((gb.loc[m].index.year//7)*7)[f"t_oc{h}"].mean()*100
        print(f"   {k:34s} h{h} n={n:4d} {x.mean()*100:+.3f}% (all {gb[f't_oc{h}'].mean()*100:+.3f}) P(down) {(x<0).mean():.2f} t={t:+.2f} | " + " ".join(f"{y}:{v:+.2f}" for y, v in byd.items()))
for col in ("basis_z", "basis_chg", "oi_chg5", "oi_z"):
    for h in (1, 5):
        m = gb[col].notna() & gb[f"t_oc{h}"].notna()
        print(f"   corr({col}, next oc{h}) = {np.corrcoef(gb.loc[m, col], gb.loc[m, f't_oc{h}'])[0,1]:+.3f}")

# ───────── C. Holidays (a weekday with no session = exchange holiday)
idx = f.index; nxt = pd.Series(idx, index=idx).shift(-1); prv = pd.Series(idx, index=idx).shift(1)
bdays_to_next = np.busday_count(idx.values.astype("datetime64[D]"), nxt.fillna(idx[-1]).values.astype("datetime64[D]"))
bdays_from_prev = np.busday_count(prv.fillna(idx[0]).values.astype("datetime64[D]"), idx.values.astype("datetime64[D]"))
f["pre_holiday"] = (bdays_to_next >= 2)   # next session skips at least one weekday
f["post_holiday"] = (bdays_from_prev >= 2)
f["pre_long_weekend"] = (bdays_to_next >= 2) & (f.dow >= 3)
print(f"\nC. HOLIDAYS: pre-holiday sessions {int(f.pre_holiday.sum())}, post-holiday {int(f.post_holiday.sum())}")
for k, m in {"pre-holiday session (decided evening before -> next open->close is the pre-holiday day)": f.pre_holiday.shift(-1).fillna(False).astype(bool),
             "post-holiday session is next": f.post_holiday.shift(-1).fillna(False).astype(bool),
             "pre-holiday session itself, open->close same day": f.pre_holiday}.items():
    col = "oc" if "same day" in k else "t_oc1"
    x = f.loc[m, col].dropna(); t, n = tst(x)
    byd = f.loc[m].groupby((f.loc[m].index.year//8)*8)[col].mean()*100
    print(f"   {k:78s} n={n:3d} {x.mean()*100:+.3f}% P(down) {(x<0).mean():.2f} t={t:+.2f} | " + " ".join(f"{y}:{v:+.2f}" for y, v in byd.items()))
x = f.loc[f.pre_holiday.shift(-1).fillna(False).astype(bool), "t_cc1"]; t, n = tst(x)
print(f"   pre-holiday day close->close                                                     n={n:3d} {x.mean()*100:+.3f}% P(down) {(x<0).mean():.2f} t={t:+.2f}")

# ───────── D. Monthly time-series momentum (decision at month end, hold next month)
mclose = w["close"].resample("ME").last(); mret = np.log(mclose).diff()
print(f"\nD. MONTHLY MOMENTUM: {len(mret.dropna())} months {mclose.index[0].date()}..{mclose.index[-1].date()}; P(month up) = {(mret.dropna()>0).mean():.3f}")
for lb in (1, 3, 6, 12):
    sig = np.log(mclose).diff(lb).shift(1)   # past lb-month return, known at month end
    m = sig.notna() & mret.notna()
    up = sig[m] > 0; hit = ((up & (mret[m] > 0)) | (~up & (mret[m] < 0))).mean()
    xpos = mret[m][up]; xneg = mret[m][~up]; tp, npos = tst(xpos); tn, nneg = tst(xneg)
    print(f"   lookback {lb:2d}m: direction hit rate {hit:.3f} (n={m.sum()}) | after positive: next month {xpos.mean()*100:+.2f}% P(down) {(xpos<0).mean():.2f} n={npos} t={tp:+.2f} | after negative: {xneg.mean()*100:+.2f}% P(down) {(xneg<0).mean():.2f} n={nneg} t={tn:+.2f}")
# combine: 12m negative AND September-ish? and MA200 at month end
ma200m = (w["close"]/w["close"].rolling(200).mean()-1).resample("ME").last().shift(1)
for k, m in {"below MA200 at month end": ma200m < 0, "above MA200 at month end": ma200m > 0,
             "below MA200 & 12m return < 0": (ma200m < 0) & (np.log(mclose).diff(12).shift(1) < 0)}.items():
    mm = m & mret.notna(); x = mret[mm]; t, n = tst(x)
    byd = x.groupby((x.index.year//8)*8).mean()*100
    print(f"   {k:34s} next month {x.mean()*100:+.2f}% P(down) {(x<0).mean():.2f} n={n} t={t:+.2f} | " + " ".join(f"{y}:{v:+.2f}" for y, v in byd.items()))

# ───────── E. Walk-forward models with the enlarged feature set, SAME-DAY target (decide at 9:01)
g = g.join(f[["pre_holiday", "post_holiday", "gap_t", "spx_prev", "dax_prev", "vixchg_prev"]], rsuffix="_dup")
g["pre_holiday_t"] = g.pre_holiday.astype(float); g["post_holiday_t"] = g.post_holiday.astype(float)
g["gap_x_spx"] = g.gap_t * g.spx_prev
# features known at 9:01 of day t: everything from row t-1 (lagged WIG20 features), gap_t, foreign t-1, basis t-1
lagged = [c for c in F.FEATURES_WIG if c not in ("dow", "month", "next_is_monday", "turn_of_month", "expiry_week")]
X = g[lagged].shift(1).add_prefix("L_")
X = X.join(g[["gap_t", "spx_prev", "dax_prev", "vixchg_prev", "gap_x_spx", "pre_holiday_t", "post_holiday_t", "dow", "month", "turn_of_month", "expiry_week"]])
X = X.join(g[["basis_z", "basis_chg", "oi_chg5", "oi_z", "fvol_z"]].shift(1))
y = (g["oc_t"] < 0).astype(int); ok = g["oc_t"].notna() & X["L_r60"].notna()
X, y, dates = X[ok].values.astype(float), y[ok].values, g.index[ok]
N = len(y); MIN_TRAIN, REFIT = 1500, 126
pl = np.full(N, np.nan); pg = np.full(N, np.nan)
for s in range(MIN_TRAIN, N, REFIT):
    tr = np.arange(0, s - 1); te = np.arange(s, min(N, s + REFIT))
    m1 = make_pipeline(SimpleImputer(), StandardScaler(), LogisticRegression(C=0.05, max_iter=2000)).fit(X[tr], y[tr])
    m2 = make_pipeline(SimpleImputer(strategy="median"), HistGradientBoostingClassifier(max_depth=3, learning_rate=0.04, max_iter=250, l2_regularization=1.0, min_samples_leaf=40, random_state=0)).fit(X[tr], y[tr])
    pl[te] = m1.predict_proba(X[te])[:, 1]; pg[te] = m2.predict_proba(X[te])[:, 1]
m = ~np.isnan(pl); pe = (pl + pg)/2
print(f"\nE. SAME-DAY WALK-FORWARD (decide 9:01 with the gap known, trade open->close): {m.sum()} OOS sessions {dates[m][0].date()}..{dates[m][-1].date()}")
for name, p in (("logistic", pl), ("boosting", pg), ("ensemble", pe)):
    auc = roc_auc_score(y[m], p[m]); acc = ((p[m] > 0.5) == y[m]).mean()
    print(f"   {name:9s} AUC {auc:.3f} accuracy {acc:.3f} (base P(down) {y[m].mean():.3f})")
oc = g.loc[dates[m], "oc_t"].values
for thr in (0.5, 0.55, 0.6, 0.65):
    sel = pe[m] > thr; r = -oc[sel] - 0.001
    yrs = pd.Series(r, index=dates[m][sel]).groupby(lambda d: (d.year//5)*5).mean()*100
    print(f"   short when P(down)>{thr}: n={sel.sum()} avg net {r.mean()*100:+.3f}% win {(r>0).mean():.2f} | " + " ".join(f"{yy}:{v:+.2f}" for yy, v in yrs.items()))
# by-era AUC
for era, (a, b) in {"2001-08": ("2001", "2008"), "2009-16": ("2009", "2016"), "2017-26": ("2017", "2026")}.items():
    mm = m & (dates >= a) & (dates <= f"{b}-12-31")
    print(f"   ensemble AUC {era}: {roc_auc_score(y[mm], pe[mm]):.3f} (n={mm.sum()})")
pd.DataFrame({"date": dates[m], "p_lr": pl[m], "p_gb": pg[m], "p_ens": pe[m], "oc_t": oc, "gap_t": g.loc[dates[m], "gap_t"].values}).to_csv("research/wig20_model/sameday_predictions.csv", index=False)
