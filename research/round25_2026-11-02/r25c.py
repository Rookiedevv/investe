# Round 25c: Cognor (and Stalprodukt) after a big US HRC steel month - robustness: signal lagged 1 day (US close is after Warsaw close),
# entry at the next session's close, own-momentum control, t-stat, both periods, 21-session hold.
import os, sys
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
exec(open(os.path.join(H, 'r25a.py')).read().split('PAIRS = [')[0])
me = [idx.get_loc(d) for d in pd.Series(idx, index=idx).groupby(idx.to_period('M')).last().values]
D = fx('HRC=F')
for t in ('COG', 'STP'):
    rows = []
    for a in me:
        s0, e0 = a - 1, a + 1                      # signal: HRC change over the 21 sessions to the day before month end; entry next session close
        if s0 < 63 or e0 + 21 >= len(idx): continue
        p0, p1 = AD[t].iloc[e0], AD[t].iloc[e0 + 21]
        if not (np.isfinite(p0) and np.isfinite(p1) and np.isfinite(D.iloc[s0]) and np.isfinite(D.iloc[s0 - 21])): continue
        x = (p1 / p0 - 1) * 100 - cst(t, e0) - ((BEN.iloc[e0 + 21] / BEN.iloc[e0] - 1) * 100 - 0.78)
        own = (AD[t].iloc[a] / AD[t].iloc[a - 21] - 1) * 100 - (W.iloc[a] / W.iloc[a - 21] - 1) * 100
        rows.append(dict(d=idx[e0], s=(D.iloc[s0] / D.iloc[s0 - 21] - 1) * 100, own=own, x=x))
    g = pd.DataFrame(rows)
    print(f"\n{t}: months {len(g)}, unconditional vs ETF {g.x.mean():+.2f}pp beats {100*(g.x>0).mean():.0f}% | corr(signal, next) {g.s.corr(g.x):+.2f} | corr(own past month, next) {g.own.corr(g.x):+.2f}")
    for th in (5, 7.5, 10, 12.5, 15):
        h = g[g.s >= th]; y = h.d.dt.year
        tt = h.x.mean() / h.x.std() * np.sqrt(len(h)) if len(h) > 2 else np.nan
        print(f"  HRC >= +{th:4.1f}%: n={len(h):3d} vs ETF {h.x.mean():+5.2f}pp med {h.x.median():+5.2f} t {tt:4.1f} beats {100*(h.x>0).mean():3.0f}% | <2022 {h.x[y<2022].mean():+5.2f} (n={(y<2022).sum()}) 2022+ {h.x[y>=2022].mean():+5.2f} (n={(y>=2022).sum()}) "
              f"| own up >3pp {h[h.own>3].x.mean():+5.2f} (n={(h.own>3).sum()}) own not up {h[h.own<=3].x.mean():+5.2f} (n={(h.own<=3).sum()})")
    h = g[g.s >= 10]; print('  HRC>=10% months:', ', '.join(f"{d:%Y-%m} {x:+.0f}" for d, x in zip(h.d, h.x)))
    k = g[g.own > 10]; print(f"  placebo - own stock up >10pp vs WIG20 last month (any HRC): n={len(k)} next {k.x.mean():+.2f}pp beats {100*(k.x>0).mean():.0f}%")
