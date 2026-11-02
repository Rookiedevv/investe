# Round 22a: financial-investor threshold crossings (5/10/15%...) on GPW -> buy at the first tradable price after the news, hold 21 sessions.
# Benchmarks: WIG20 TR ETF same dates (WIG20 + 3.5%/yr before Feb 2019), same-stock random 21-session holds, deposit 0.45%/month.
import os, sys, glob
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '..', 'round9_2026-10-30'))

from lib import *  # P, W, CL, AD, VO, idx, TURN

ETF = pd.read_csv(R + '/data/prices/ETFBW20TR.csv', parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
OP = pd.DataFrame({t: P[t]['open'] for t in TICK}).reindex(idx)
FAC = AD / CL                      # adjustment factor so opens are comparable with adj closes
AOP = OP * FAC

def bench(i0, i1):
    if idx[i0] >= pd.Timestamp('2019-02-01'):
        r = (ETF.iloc[i1] / ETF.iloc[i0] - 1) * 100
    else:
        r = (W.iloc[i1] / W.iloc[i0] - 1) * 100 + 3.5 * (i1 - i0) / 252
    return r - 0.78                # ETF round-trip cost

def cst(t, i):
    tv = TURN[t].iloc[i]
    if not np.isfinite(tv): return 2.7
    return float(np.select([tv > 30e6, tv > 10e6, tv > 3e6, tv > 1e6], [0.9, 1.0, 1.3, 2.0], 2.7))

HOLD = int(os.environ.get('HOLD', 21))
rng = np.random.default_rng(21); RAND = {}
def own_rand(t, hold=HOLD, k=300):
    s = AD[t].dropna(); a = idx.get_loc(s.index[0]); b = idx.get_loc(s.index[-1]) - hold - 1
    v = []
    for _ in range(k):
        i = int(rng.integers(a, b)); p0, p1 = AD[t].iloc[i], AD[t].iloc[i + hold]
        if np.isfinite(p0) and np.isfinite(p1): v.append((p1 / p0 - 1) * 100 - cst(t, i) - bench(i, i + hold))
    return float(np.mean(v))

# ---- events
fs = sorted(glob.glob(os.path.join(H, 'stakes_*.csv')))
ev = pd.concat([pd.read_csv(f, dtype=str) for f in fs], ignore_index=True)
ev['date'] = pd.to_datetime(ev['date'], errors='coerce'); ev = ev.dropna(subset=['date'])
ev['ticker'] = ev.ticker.str.strip().str.upper()
for c in ('direction', 'holder_type', 'cause'): ev[c] = ev[c].fillna('unknown').str.strip().str.lower()
for c in ('threshold', 'pct_before', 'pct_after'): ev[c] = pd.to_numeric(ev[c], errors='coerce')
ev['holder'] = ev.holder.fillna('')
ev = ev.drop_duplicates(['date', 'ticker', 'holder', 'direction']).sort_values('date')
print('events', len(ev), '| with prices', ev.ticker.isin(AD.columns).sum(), '| dir', ev.direction.value_counts().to_dict(),
      '| cause', ev.cause.value_counts().to_dict(), '| type', ev.holder_type.value_counts().to_dict())

rows = []
for _, e in ev.iterrows():
    t = e.ticker
    if t not in AD.columns: continue
    d = e.date; tm = str(e.session_timing).strip().lower()
    i = idx.searchsorted(d)
    if i >= len(idx) or i < 1: continue
    if idx[i] != d: tm = 'before'
    if tm == 'before':   ie, px = i, AOP[t].iloc[i]
    elif tm == 'during': ie, px = i, AD[t].iloc[i]
    elif tm == 'after':  ie, px = i + 1, AOP[t].iloc[i + 1] if i + 1 < len(idx) else np.nan
    else:                ie, px = i + 1, AD[t].iloc[i + 1] if i + 1 < len(idx) else np.nan
    ix = ie + HOLD
    if ix >= len(idx) or not np.isfinite(px) or not np.isfinite(AD[t].iloc[ix]): continue
    pb = AD[t].iloc[i - 1]
    react = (px / pb - 1) * 100 - (W.iloc[ie] / W.iloc[i - 1] - 1) * 100 if np.isfinite(pb) else np.nan
    # move from 21 sessions before the notice to the close before it (what the fund's buying/selling already did)
    pre = (AD[t].iloc[i - 1] / AD[t].iloc[max(i - 22, 0)] - 1) * 100 - (W.iloc[i - 1] / W.iloc[max(i - 22, 0)] - 1) * 100
    gross = (AD[t].iloc[ix] / px - 1) * 100
    r = gross - cst(t, ie)
    b = bench(ie - 1 if tm in ('before', 'after') else ie, ix)
    sh = -gross - (0.6 + cst(t, ie) - 0.78 + 0.7 * HOLD / 252)        # XTB short, absolute net
    if t not in RAND: RAND[t] = own_rand(t)
    rows.append(dict(t=t, d=idx[ie], dirn=e.direction, ht=e.holder_type, cause=e.cause, thr=e.threshold, holder=str(e.holder)[:40],
                     tm=tm, react=react, pre=pre, r=r, x=r - b, sh=sh, ctl=RAND[t], turn=TURN[t].iloc[ie], dep=0.45 * HOLD / 21))
df = pd.DataFrame(rows)
df.to_csv(os.path.join(H, f'r22a_trades_h{HOLD}.csv'), index=False)

def rep(g, lab):
    if len(g) < 4: print(f"{lab:50s} n={len(g)}"); return
    y = g.d.dt.year; tt = g.x.mean() / g.x.std() * np.sqrt(len(g))
    print(f"{lab:50s} n={len(g):3d} net {g.r.mean():+5.2f}% | vs ETF {g.x.mean():+5.2f}pp med {g.x.median():+5.2f} t {tt:4.1f} "
          f"beats {100*(g.x>0).mean():3.0f}% | <2021 {g.x[y<2021].mean():+5.2f} (n={int((y<2021).sum())}) 2021+ {g.x[y>=2021].mean():+5.2f} "
          f"| excess {g.x.mean()-g.ctl.mean():+5.2f} | react {g.react.mean():+4.1f} pre21 {g.pre.mean():+4.1f} | XTB short {g.sh.mean():+5.2f}% win {100*(g.sh>0).mean():3.0f}%")

clean = df[df.cause.isin(['market', 'unknown', 'index'])]
print(f'\n== first tradable price after the notice, hold {HOLD} (long = net of eMakler costs; short = XTB)')
for dn in ('up', 'down'):
    a = df[df.dirn == dn]; c = clean[clean.dirn == dn]
    print(f'-- {dn}')
    rep(a, 'all causes'); rep(c, 'market/unknown cause only')
    for k in ('ofe', 'tfi', 'foreign_am', 'other_financial'): rep(c[c.ht == k], '  ' + k)
    rep(c[c.thr >= 10], '  threshold >= 10%'); rep(c[c.thr < 10], '  threshold 5%')
    rep(c[c.turn > 3e6], '  liquid (> 3m PLN/day)'); rep(c[c.turn <= 3e6], '  illiquid')
    rep(c[~c.holder.str.contains('BlackRock', case=False)], '  excl. BlackRock')
    rep(c[c.pre > 5], '  stock already +5% vs WIG20 over prior month'); rep(c[c.pre <= 5], '  not already up')
    for k in ('before', 'during', 'after', 'unknown'): rep(c[c.tm == k], '  timing ' + k)
for k in ('abb', 'tender', 'ipo', 'capital_change', 'merger'): rep(df[df.cause == k], 'cause ' + k)
print('\nper-ticker:', df.t.value_counts().to_dict())
