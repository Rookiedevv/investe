# Round 25b: Grupa Azoty after a gas (TTF) rise -> next month; unconditional baseline, fixed thresholds, XTB short, both periods
import os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
exec(open(os.path.join(H, 'r25a.py')).read().split('PAIRS = [')[0])
STOCK = os.environ.get('STOCK', 'ATT'); DRV = os.environ.get('DRV', 'TTF=F')
D = fx(DRV); t = STOCK
me = [idx.get_loc(d) for d in pd.Series(idx, index=idx).groupby(idx.to_period('M')).last().values]
rows = []
for a, b in zip(me[:-1], me[1:]):
    if a < 63: continue
    p0, p1 = AD[t].iloc[a], AD[t].iloc[b]
    if not (np.isfinite(p0) and np.isfinite(p1) and np.isfinite(D.iloc[a]) and np.isfinite(D.iloc[a - 21])): continue
    g = (p1 / p0 - 1) * 100; bm = (BEN.iloc[b] / BEN.iloc[a] - 1) * 100
    sh = -g - (0.6 + cst(t, a) - 0.78 + 0.7 * (b - a) / 252)     # XTB short, absolute net
    rows.append(dict(d=idx[a], s1=(D.iloc[a] / D.iloc[a - 21] - 1) * 100, x=g - cst(t, a) - (bm - 0.78), sh=sh, shx=sh + bm,  # shx: short + ETF long (hedged)
                     dep=0.45))
g = pd.DataFrame(rows); y = g.d.dt.year
print(f"{t} vs {DRV}: months {len(g)} ({g.d.min():%Y-%m}..{g.d.max():%Y-%m}); unconditional next month vs ETF {g.x.mean():+.2f}pp, lags {100*(g.x<0).mean():.0f}%, XTB short {g.sh.mean():+.2f}% win {100*(g.sh>0).mean():.0f}%")
for th in (5, 10, 15, 20, 30):
    for side, sel in (('rise', g.s1 >= th), ('fall', g.s1 <= -th)):
        h = g[sel]
        if len(h) < 5: continue
        a, b = h[h.d.dt.year < 2022], h[h.d.dt.year >= 2022]
        print(f"  gas {side} >= {th:2d}% last month: n={len(h):3d} | {t} next month vs ETF {h.x.mean():+5.2f}pp (med {h.x.median():+5.2f}) lags {100*(h.x<0).mean():3.0f}% "
              f"| XTB short {h.sh.mean():+5.2f}% win {100*(h.sh>0).mean():3.0f}% beats deposit {100*(h.sh>h.dep).mean():3.0f}% | <2022 {a.x.mean():+5.2f} (n={len(a)}) 2022+ {b.x.mean():+5.2f} (n={len(b)})")
g.to_csv(os.path.join(H, f'r25b_{t}_{DRV}.csv'), index=False)
