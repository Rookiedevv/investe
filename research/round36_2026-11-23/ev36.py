"""Round 36: event-time test - buy after a quarterly report with a strong y/y profit change, hold N sessions."""
from lib36 import *
import fund36 as F
Q = F.Q[F.Q.pub_known].copy()
def run(hold=21, off=1, mint=2e6, maxt=None, start='2011-01-01'):
    rows = []
    for r_ in Q.itertuples():
        if r_.ticker not in AD or r_.avail < pd.Timestamp(start): continue
        i = idx.searchsorted(r_.avail, side='right') - 1 + off     # off=1: first session strictly after the publication date
        if i + hold >= len(idx) or i < 60: continue
        if (idx[i] - r_.avail).days > 7: continue
        tv = TURN[r_.ticker].iloc[i]
        if not np.isfinite(tv) or tv < mint or (maxt and tv >= maxt): continue
        a, b = AD[r_.ticker].iloc[i], AD[r_.ticker].ffill(limit=10).iloc[i + hold]
        if not (np.isfinite(a) and np.isfinite(b)): continue
        c = float(np.select([tv > 30e6, tv > 10e6, tv > 3e6, tv > 1e6], [0.9, 1.0, 1.3, 2.0], 2.7))
        net = (b / a - 1) * 100 - c; w = wig(i, i + hold) - ETF_COST
        # price reaction: close before publication day -> close of entry day, vs WIG
        j0 = idx.searchsorted(r_.avail, side='left') - 1
        react = (AD[r_.ticker].iloc[i] / AD[r_.ticker].iloc[j0] - 1) * 100 - wig(j0, i) if j0 >= 0 else np.nan
        pre = (AD[r_.ticker].iloc[j0] / AD[r_.ticker].iloc[j0 - 21] - 1) * 100 - wig(j0 - 21, j0) if j0 >= 21 else np.nan
        rows.append(dict(t=r_.ticker, d=idx[i], pub=r_.avail, period=r_.period, net=net, xw=net - w, turn=tv, fin=r_.FIN, sue=r_.sue, d_ni=r_.d_ni, d_rev=r_.d_rev, d_ebit=r_.d_ebit, d_margin=r_.d_margin, roe=r_.roe, react=react, pre=pre, ni=r_.NI, q=r_.q))
    return pd.DataFrame(rows)
def rep(df, lab, split='2019-01-01'):
    if len(df) < 5: print(f"{lab:46s} n={len(df)}"); return
    x = df.xw; y = pd.to_datetime(df.d)
    # t-stat clustered by entry month (reports cluster in seasons)
    mm = x.groupby([y.dt.year, y.dt.month]).mean(); tc = tstat(mm)
    a, b = x[y < split], x[y >= split]
    print(f"{lab:46s} n={len(df):4d} net {df.net.mean():+5.1f}% | vsWIG {x.mean():+5.2f}pp med {x.median():+5.2f} beats {100*(x>0).mean():3.0f}% t(by month) {tc:4.1f} | <2019 {a.mean():+5.1f} ({len(a)}) 2019+ {b.mean():+5.1f} ({len(b)})")
if __name__ == '__main__':
    D = run(); D.to_pickle('ev21.pkl')
    print('reports of liquid stocks with entry:', len(D), 'tickers', D.t.nunique(), D.d.min().date(), D.d.max().date())
    rep(D, 'all reports (baseline)')
    for lab, m in (('SUE >= 2', D.sue >= 2), ('SUE >= 1', D.sue >= 1), ('SUE 0..1', (D.sue >= 0) & (D.sue < 1)), ('SUE -1..0', (D.sue < 0) & (D.sue >= -1)), ('SUE <= -1', D.sue <= -1), ('SUE <= -2', D.sue <= -2),
                   ('d_ni >= +3% of equity', D.d_ni >= .03), ('d_ni >= +1.5%', D.d_ni >= .015), ('d_ni 0..1.5%', (D.d_ni >= 0) & (D.d_ni < .015)), ('d_ni -1.5..0', (D.d_ni < 0) & (D.d_ni >= -.015)), ('d_ni <= -1.5%', D.d_ni <= -.015), ('d_ni <= -3%', D.d_ni <= -.03),
                   ('rev y/y >= +20%', D.d_rev >= .2), ('rev y/y <= -10%', D.d_rev <= -.1), ('d_ebit top (>= +1% of assets)', D.d_ebit >= .01), ('d_ebit <= -1%', D.d_ebit <= -.01),
                   ('SUE>=1 & d_ni>=1.5%', (D.sue >= 1) & (D.d_ni >= .015)), ('SUE<=-1 & d_ni<=-1.5%', (D.sue <= -1) & (D.d_ni <= -.015))):
        rep(D[m], lab)
