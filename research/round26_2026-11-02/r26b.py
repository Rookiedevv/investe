# Round 26b: Orlen after a rise in the diesel crack spread - robustness (thresholds in USD/bbl, holds, own momentum, Brent control, years)
import os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
exec(open(os.path.join(H, 'r26a.py')).read().split('PAIRS = [')[0])
me = [idx.get_loc(d) for d in pd.Series(idx, index=idx).groupby(idx.to_period('M')).last().values]
D = DRV['CRACK_DIESEL']; B = DRV['BZ=F']; t = 'PKN'
for hold in (10, 21, 42):
    rows = []
    for a in me:
        s0, e0 = a - 1, a + 1
        if s0 < 63 or e0 + hold >= len(idx): continue
        p0, p1 = AD[t].iloc[e0], AD[t].iloc[e0 + hold]
        if not all(np.isfinite(v) for v in (p0, p1, D.iloc[s0], D.iloc[s0 - 21])): continue
        g = (p1 / p0 - 1) * 100; bm = (BEN.iloc[e0 + hold] / BEN.iloc[e0] - 1) * 100
        rows.append(dict(d=idx[e0], s=D.iloc[s0] - D.iloc[s0 - 21], lvl=D.iloc[s0], br=(B.iloc[s0] / B.iloc[s0 - 21] - 1) * 100,
                         own=(AD[t].iloc[a] / AD[t].iloc[a - 21] - 1) * 100 - (W.iloc[a] / W.iloc[a - 21] - 1) * 100,
                         x=g - cst(t, e0) - (bm - 0.78), dep=0.45 * hold / 21))
    g = pd.DataFrame(rows)
    print(f"\n== hold {hold}: months {len(g)}, baseline {g.x.mean():+.2f}pp beats {100*(g.x>0).mean():.0f}%, corr(crack chg, next) {g.s.corr(g.x):+.2f}, partial on Brent: "
          f"{np.corrcoef(g.s - np.polyval(np.polyfit(g.br, g.s, 1), g.br), g.x)[0,1]:+.2f}")
    for th in (3, 5, 8, 10, 15):
        h = g[g.s >= th]; y = h.d.dt.year
        if len(h) < 5: continue
        tt = h.x.mean() / h.x.std() * np.sqrt(len(h))
        print(f"  crack +{th:2d} USD/bbl: n={len(h):3d} vs ETF {h.x.mean():+5.2f}pp med {h.x.median():+5.2f} t {tt:4.1f} beats {100*(h.x>0).mean():3.0f}% >dep {100*((h.x)>0).mean():3.0f}% "
              f"| <2021 {h.x[y<2021].mean():+5.2f} (n={(y<2021).sum()}) 2021+ {h.x[y>=2021].mean():+5.2f} (n={(y>=2021).sum()}) | ex-2022 {h.x[y!=2022].mean():+5.2f} (n={(y!=2022).sum()}) "
              f"| own up {h[h.own>0].x.mean():+5.2f} own down {h[h.own<=0].x.mean():+5.2f}")
    if hold == 21:
        for th in (-5, -10):
            h = g[g.s <= th]; print(f"  crack {th} USD/bbl: n={len(h)} vs ETF {h.x.mean():+.2f}pp med {h.x.median():+.2f} beats {100*(h.x>0).mean():.0f}%")
        h = g[g.s >= 5]; print('  months crack >= +5:', ', '.join(f"{d:%Y-%m} {x:+.0f}" for d, x in zip(h.d, h.x)))
        print('  current: crack level %.1f USD/bbl, 21-session change to the day before the last session of Oct 2026: %+.1f' %
              (D.iloc[me[-2] - 1] if me[-1] >= len(idx) - 1 else D.iloc[me[-1] - 1], (D.iloc[me[-1] - 1] - D.iloc[me[-1] - 22])))
