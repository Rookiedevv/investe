# Round 21a: share buyback announcements on GPW -> buy at the first tradable price after the news, hold 21 sessions.
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
fs = [os.path.join(H, 'seed_known.csv')] + sorted(glob.glob(os.path.join(H, 'buybacks_*.csv')))
ev = pd.concat([pd.read_csv(f, dtype=str) for f in fs if os.path.exists(f)], ignore_index=True)
ev['date'] = pd.to_datetime(ev['date'], errors='coerce'); ev = ev.dropna(subset=['date'])
ev['ticker'] = ev.ticker.str.strip().str.upper(); ev['event_type'] = ev.event_type.str.strip()
for c in ('shares_pct', 'premium_pct', 'value_pln_m', 'price_pln'): ev[c] = pd.to_numeric(ev[c], errors='coerce')
ev = ev.drop_duplicates(['date', 'ticker', 'event_type']).sort_values('date')
ev = ev[ev.event_type != 'cancelled']
print('events', len(ev), '| with prices', ev.ticker.isin(AD.columns).sum(), '| by type', ev.event_type.value_counts().to_dict())

rows = []
for _, e in ev.iterrows():
    t = e.ticker
    if t not in AD.columns: continue
    d = e.date; tm = str(e.session_timing).strip().lower()
    i = idx.searchsorted(d)                  # first session on/after the date
    if i >= len(idx): continue
    if idx[i] != d: tm = 'before'            # weekend/holiday news -> tradable at the next open
    # entry: before -> open of day i; during -> close of day i; after -> open of i+1; unknown -> close of i+1 (conservative)
    if tm == 'before':   ie, px = i, AOP[t].iloc[i]
    elif tm == 'during': ie, px = i, AD[t].iloc[i]
    elif tm == 'after':  ie, px = i + 1, AOP[t].iloc[i + 1] if i + 1 < len(idx) else np.nan
    else:                ie, px = i + 1, AD[t].iloc[i + 1] if i + 1 < len(idx) else np.nan
    ix = ie + HOLD
    if ix >= len(idx) or not np.isfinite(px) or not np.isfinite(AD[t].iloc[ix]): continue
    pb = AD[t].iloc[i - 1]                   # close before the news
    react = (px / pb - 1) * 100 - (W.iloc[ie] / W.iloc[i - 1] - 1) * 100 if np.isfinite(pb) else np.nan
    r = (AD[t].iloc[ix] / px - 1) * 100 - cst(t, ie)
    # benchmark from the previous close when entering at an open (ETF has no open) -> use the entry day's previous close
    b = bench(ie - 1 if tm in ('before', 'after') else ie, ix)
    if t not in RAND: RAND[t] = own_rand(t)
    rows.append(dict(t=t, d=idx[ie], typ=e.event_type, tm=tm, sz=e.shares_pct, prem=e.premium_pct, val=e.value_pln_m,
                     react=react, r=r, x=r - b, ctl=RAND[t], turn=TURN[t].iloc[ie], dep=0.45 * HOLD / 21, detail=str(e.detail)[:60]))
df = pd.DataFrame(rows)
df.to_csv(os.path.join(H, f'r21a_trades_h{HOLD}.csv'), index=False)

def rep(g, lab):
    if len(g) < 4: print(f"{lab:52s} n={len(g)}"); return
    y = g.d.dt.year; tt = g.x.mean() / g.x.std() * np.sqrt(len(g))
    print(f"{lab:52s} n={len(g):3d} net {g.r.mean():+5.2f}% | vs ETF {g.x.mean():+5.2f}pp med {g.x.median():+5.2f} t {tt:4.1f} "
          f"beats {100*(g.x>0).mean():3.0f}% | >dep {100*(g.r>g.dep).mean():3.0f}% | <2022 {g.x[y<2022].mean():+5.2f} (n={int((y<2022).sum())}) "
          f"2022+ {g.x[y>=2022].mean():+5.2f} | excess {g.x.mean()-g.ctl.mean():+5.2f} | react {g.react.mean():+4.1f}")

print(f'\n== buy at first tradable price after the news, hold {HOLD} sessions (net of per-stock costs)')
rep(df, 'all buyback news')
for k in ('board_proposal', 'authorization', 'program_start', 'tender', 'incentive'): rep(df[df.typ == k], '  ' + k)
nonin = df[df.typ != 'incentive']
rep(nonin, 'all excl. incentive')
first = nonin.sort_values('d').groupby('t', group_keys=False).apply(lambda g: g[g.d.diff().dt.days.fillna(9999) > 180])
rep(first, 'first news of a programme (no buyback news in prior 180d)')
rep(nonin[nonin.sz >= 3], 'size >= 3% of shares')
rep(nonin[(nonin.sz < 3) | nonin.sz.isna()], 'size < 3% or unknown')
rep(nonin[nonin.turn > 3e6], 'liquid (turnover > 3m PLN/day)')
rep(nonin[nonin.turn <= 3e6], 'illiquid (<= 3m)')
for k in ('before', 'during', 'after', 'unknown'): rep(nonin[nonin.tm == k], '  timing ' + k)
rep(nonin[nonin.react >= 2], 'reaction to entry >= +2% vs WIG20')
rep(nonin[nonin.react < 2], 'reaction < +2%')
print('\nper-ticker counts:', nonin.t.value_counts().to_dict())
pd.set_option('display.width', 250)
print(df.sort_values('d')[['d', 't', 'typ', 'tm', 'sz', 'prem', 'react', 'r', 'x', 'detail']].round(1).to_string(index=False))
