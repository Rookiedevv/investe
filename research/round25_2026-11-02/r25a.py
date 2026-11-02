# Round 25a: gas (TTF) / steel (HRC) prices and foreign peers -> Grupa Azoty, Police, Cognor, Stalprodukt.
# (1) month-end signal: driver's past 1- and 3-month change -> stock's next month vs WIG20 TR ETF, net of costs (non-overlapping)
# (2) daily read-through: big driver/peer day -> stock over the next 1 / 5 / 21 sessions vs WIG20 (entry at next close)
import os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'round9_2026-10-30'))
from lib import *

FOR = os.path.join(R, 'research', 'prices_foreign')
def fx(sym):
    f = os.path.join(FOR, sym + '.csv')
    if not os.path.exists(f): return None
    d = pd.read_csv(f, parse_dates=['date']).set_index('date')['adj_close']
    return d[~d.index.duplicated()].reindex(idx).ffill(limit=5)
ETF = pd.read_csv(R + '/data/prices/ETFBW20TR.csv', parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
BEN = pd.Series(np.where(idx >= pd.Timestamp('2019-02-01'), np.nan, np.nan), index=idx)
# benchmark level: ETF from Feb 2019, before that WIG20 + 3.5%/yr dividends
wl = W * np.exp(np.log(1.035) * np.arange(len(idx)) / 252)
BEN = ETF.copy(); m = idx < pd.Timestamp('2019-02-01')
first = ETF.first_valid_index(); BEN[m] = wl[m] * ETF.loc[first] / wl.loc[first]

def cst(t, i):
    tv = TURN[t].iloc[i]
    if not np.isfinite(tv): return 2.7
    return float(np.select([tv > 30e6, tv > 10e6, tv > 3e6, tv > 1e6], [0.9, 1.0, 1.3, 2.0], 2.7))

PAIRS = [  # stock, driver, expected sign of the relation
    ('ATT', 'TTF=F', -1), ('PCE', 'TTF=F', -1), ('ATT', 'YAR.OL', +1), ('ATT', 'CF', +1), ('PCE', 'YAR.OL', +1),
    ('COG', 'HRC=F', +1), ('STP', 'HRC=F', +1), ('COG', 'MT.AS', +1), ('STP', 'MT.AS', +1), ('COG', 'VOE.VI', +1), ('COG', 'SZG.DE', +1),
    ('KGH', 'TTF=F', -1), ('PGE', 'TTF=F', -1),   # controls: energy-intensive / power
]

# ---- (1) month-end signal
me = pd.Series(idx, index=idx).groupby(idx.to_period('M')).last().values
me = [idx.get_loc(d) for d in me]
print('== (1) month-end: driver change over past 1m / 3m -> stock next month vs ETF (net of costs); signal tercile spread')
out = []
for t, drv, sg in PAIRS:
    if t not in AD.columns: print(t, 'no prices'); continue
    D = fx(drv)
    if D is None: print(drv, 'no data'); continue
    rows = []
    for a, b in zip(me[:-1], me[1:]):
        if a < 63: continue
        p0, p1 = AD[t].iloc[a], AD[t].iloc[b]
        if not (np.isfinite(p0) and np.isfinite(p1) and np.isfinite(D.iloc[a]) and np.isfinite(D.iloc[a - 21]) and np.isfinite(D.iloc[a - 63])): continue
        x = (p1 / p0 - 1) * 100 - cst(t, a) - ((BEN.iloc[b] / BEN.iloc[a] - 1) * 100 - 0.78)
        rows.append(dict(d=idx[a], s1=(D.iloc[a] / D.iloc[a - 21] - 1) * 100, s3=(D.iloc[a] / D.iloc[a - 63] - 1) * 100, x=x,
                         same=(p0 / AD[t].iloc[a - 21] - 1) * 100))
    g = pd.DataFrame(rows)
    if len(g) < 24: print(t, drv, 'n', len(g)); continue
    for col in ('s1', 's3'):
        c = g[col].corr(g.x); q = g[col].quantile([1/3, 2/3]).values
        hi, lo = g[g[col] >= q[1]].x, g[g[col] <= q[0]].x
        good = hi if sg > 0 else lo; bad = lo if sg > 0 else hi
        y = g.d.dt.year
        c_a = g[y < 2022][col].corr(g[y < 2022].x); c_b = g[y >= 2022][col].corr(g[y >= 2022].x)
        out.append((t, drv, col, len(g), c, c_a, c_b, good.mean(), (good > 0).mean() * 100, bad.mean(), (bad < 0).mean() * 100))
        print(f"{t:4s} {drv:7s} {col} n={len(g):3d} corr {c:+.2f} (<2022 {c_a:+.2f}, 2022+ {c_b:+.2f}) | expected-good tercile {good.mean():+5.2f}pp beats {100*(good>0).mean():3.0f}% "
              f"| expected-bad tercile {bad.mean():+5.2f}pp lags {100*(bad<0).mean():3.0f}% (first {g.d.min():%Y-%m})")

# ---- (2) daily read-through: driver/peer day move z >= 2 (vs 60-day SD) while the stock moved < 1 SD same day
print('\n== (2) big driver day (|z| >= 2) -> stock from next close, vs WIG20 (gross, before costs), signed by expected relation')
for t, drv, sg in PAIRS:
    if t not in AD.columns: continue
    D = fx(drv)
    if D is None: continue
    dr = D.pct_change() * 100; z = dr / dr.rolling(60).std()
    sr = AD[t].pct_change() * 100; zs = (sr - W.pct_change() * 100) / sr.rolling(60).std()
    res = {}
    for k in (1, 5, 21):
        v = []
        for i in np.where((z.abs() >= 2).values)[0]:
            if i + 1 + k >= len(idx) or abs(zs.iloc[i]) > 1: continue
            p0, p1 = AD[t].iloc[i + 1], AD[t].iloc[i + 1 + k]
            if not (np.isfinite(p0) and np.isfinite(p1)): continue
            ex = (p1 / p0 - 1) * 100 - (W.iloc[i + 1 + k] / W.iloc[i + 1] - 1) * 100
            v.append(np.sign(z.iloc[i]) * sg * ex)     # positive = moved the way the driver implies
        v = np.array(v); res[k] = (len(v), v.mean() if len(v) else np.nan, (v > 0).mean() * 100 if len(v) else np.nan)
    print(f"{t:4s} {drv:7s} n={res[1][0]:3d} | next 1d {res[1][1]:+.2f}% ({res[1][2]:.0f}% right) | 5d {res[5][1]:+.2f}% ({res[5][2]:.0f}%) | 21d {res[21][1]:+.2f}% ({res[21][2]:.0f}%)")
pd.DataFrame(out, columns=['stock', 'driver', 'sig', 'n', 'corr', 'corr_pre2022', 'corr_2022p', 'good_terc_pp', 'good_beats', 'bad_terc_pp', 'bad_lags']).round(2).to_csv(os.path.join(H, 'r25a_monthly.csv'), index=False)
