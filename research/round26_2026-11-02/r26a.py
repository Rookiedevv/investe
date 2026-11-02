# Round 26a: more price drivers -> GPW stocks, month-end signal with a 1-day lag (US settlements come after the Warsaw close).
# Signal = driver change over the 21 sessions to the day BEFORE the last session of the month; entry at the close of the first
# session of the next month; hold 21 sessions; net of per-stock costs; vs WIG20 TR ETF (WIG20 + 3.5%/yr before Feb 2019).
import os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'round9_2026-10-30'))
from lib import *

FOR = os.path.join(R, 'research', 'prices_foreign')
def fx(sym):
    f = os.path.join(FOR, sym + '.csv')
    if not os.path.exists(f): return None
    d = pd.read_csv(f, parse_dates=['date']).set_index('date')['adj_close']
    d = d[~d.index.duplicated()]
    d = d[d > 0]
    return d.reindex(idx).ffill(limit=5)
ETF = pd.read_csv(R + '/data/prices/ETFBW20TR.csv', parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
wl = W * np.exp(np.log(1.035) * np.arange(len(idx)) / 252)
BEN = ETF.copy(); m = idx < pd.Timestamp('2019-02-01'); f0 = ETF.first_valid_index(); BEN[m] = wl[m] * ETF.loc[f0] / wl.loc[f0]
def cst(t, i):
    tv = TURN[t].iloc[i]
    if not np.isfinite(tv): return 2.7
    return float(np.select([tv > 30e6, tv > 10e6, tv > 3e6, tv > 1e6], [0.9, 1.0, 1.3, 2.0], 2.7))

DRV = {k: fx(k) for k in ('ALI=F', 'SI=F', 'BTC-USD', 'HO=F', 'RB=F', 'BZ=F', 'HG=F')}
if DRV['HO=F'] is not None and DRV['BZ=F'] is not None:
    DRV['CRACK_DIESEL'] = DRV['HO=F'] * 42 - DRV['BZ=F']       # USD/bbl
    DRV['CRACK_GASOLINE'] = DRV['RB=F'] * 42 - DRV['BZ=F']
if DRV['BTC-USD'] is not None:
    br = np.log(DRV['BTC-USD']).diff()
    DRV['BTC_VOL'] = br.rolling(21).std() * np.sqrt(365) * 100   # annualised realised vol, level
if DRV['SI=F'] is not None and DRV.get('HG=F') is not None: pass

PAIRS = [('KTY', 'ALI=F', +1), ('KGH', 'SI=F', +1), ('XTB', 'BTC-USD', +1), ('XTB', 'BTC_VOL', +1),
         ('PKN', 'CRACK_DIESEL', +1), ('PKN', 'CRACK_GASOLINE', +1), ('UNT', 'CRACK_DIESEL', +1), ('PKN', 'BZ=F', -1)]
LEVEL = {'CRACK_DIESEL', 'CRACK_GASOLINE', 'BTC_VOL'}            # change measured in points (level difference), not %

me = [idx.get_loc(d) for d in pd.Series(idx, index=idx).groupby(idx.to_period('M')).last().values]
summary = []
for t, dn, sg in PAIRS:
    D = DRV.get(dn)
    if D is None or t not in AD.columns: print(t, dn, 'no data'); continue
    rows = []
    for a in me:
        s0, e0 = a - 1, a + 1
        if s0 < 63 or e0 + 21 >= len(idx): continue
        p0, p1 = AD[t].iloc[e0], AD[t].iloc[e0 + 21]
        d0, d1 = D.iloc[s0 - 21], D.iloc[s0]
        if not all(np.isfinite(v) for v in (p0, p1, d0, d1)): continue
        s = (d1 - d0) if dn in LEVEL else (d1 / d0 - 1) * 100
        g = (p1 / p0 - 1) * 100; bm = (BEN.iloc[e0 + 21] / BEN.iloc[e0] - 1) * 100
        rows.append(dict(d=idx[e0], s=s, lvl=d1, x=g - cst(t, e0) - (bm - 0.78), sh=-g - (0.6 + cst(t, e0) - 0.78 + 0.7 * 21 / 252)))
    g = pd.DataFrame(rows)
    if len(g) < 24: print(t, dn, 'n', len(g)); continue
    y = g.d.dt.year; c = g.s.corr(g.x)
    ca, cb = g[y < 2021].s.corr(g[y < 2021].x), g[y >= 2021].s.corr(g[y >= 2021].x)
    print(f"\n{t} <- {dn} (expected sign {sg:+d}): months {len(g)} from {g.d.min():%Y-%m} | corr {c:+.2f} (<2021 {ca:+.2f}, 2021+ {cb:+.2f}) | "
          f"baseline vs ETF {g.x.mean():+.2f}pp beats {100*(g.x>0).mean():.0f}%")
    q = g.s.quantile([0.2, 1/3, 2/3, 0.8]).values
    for lab, sel in (('top 20% of signal', g.s >= q[3]), ('top third', g.s >= q[2]), ('bottom third', g.s <= q[1]), ('bottom 20%', g.s <= q[0])):
        h = g[sel]; yy = h.d.dt.year; tt = h.x.mean() / h.x.std() * np.sqrt(len(h))
        print(f"   {lab:18s} n={len(h):3d} next month vs ETF {h.x.mean():+5.2f}pp med {h.x.median():+5.2f} t {tt:4.1f} beats {100*(h.x>0).mean():3.0f}% "
              f"| <2021 {h.x[yy<2021].mean():+5.2f} 2021+ {h.x[yy>=2021].mean():+5.2f} | XTB short {h.sh.mean():+5.2f}% win {100*(h.sh>0).mean():3.0f}%")
        summary.append((t, dn, lab, len(h), h.x.mean(), h.x.median(), (h.x > 0).mean() * 100, h.x[yy < 2021].mean(), h.x[yy >= 2021].mean(), h.sh.mean()))
    if dn in LEVEL:   # also the level itself (e.g. high crack spread / high bitcoin vol regimes)
        ql = g.lvl.quantile([1/3, 2/3]).values
        for lab, sel in (('level top third', g.lvl >= ql[1]), ('level bottom third', g.lvl <= ql[0])):
            h = g[sel]; print(f"   {lab:18s} n={len(h):3d} next month vs ETF {h.x.mean():+5.2f}pp med {h.x.median():+5.2f} beats {100*(h.x>0).mean():3.0f}%")

# ---- daily read-through: big driver day (|z| >= 2 vs 60-day SD) known before the next Warsaw session -> stock from next OPEN-ish
# (use the next session's close-to-close, i.e. entry at the close of the session after the US move: conservative)
print('\n== daily: big driver day -> stock, entry at the close of the next Warsaw session, signed by expected relation (gross, vs WIG20)')
for t, dn, sg in PAIRS:
    D = DRV.get(dn)
    if D is None or t not in AD.columns or dn in LEVEL: continue
    dr = D.pct_change() * 100; z = dr / dr.rolling(60).std()
    for k in (1, 5, 21):
        v = []
        for i in np.where((z.abs() >= 2).values)[0]:
            if i + 1 + k >= len(idx): continue
            p0, p1 = AD[t].iloc[i + 1], AD[t].iloc[i + 1 + k]
            if not (np.isfinite(p0) and np.isfinite(p1)): continue
            v.append(np.sign(z.iloc[i]) * sg * ((p1 / p0 - 1) * 100 - (W.iloc[i + 1 + k] / W.iloc[i + 1] - 1) * 100))
        v = np.array(v)
        print(f"{t:4s} {dn:8s} k={k:2d} n={len(v):3d} mean {v.mean():+.2f}% right {100*(v>0).mean():.0f}%", end=' | ' if k < 21 else '\n')
pd.DataFrame(summary, columns=['stock', 'driver', 'bucket', 'n', 'vs_etf', 'median', 'beats', 'pre2021', 'from2021', 'xtb_short']).round(2).to_csv(os.path.join(H, 'r26a_summary.csv'), index=False)
