# Round 24a: board dividend proposals vs last year (raise / cut / first / skipped) on GPW -> buy at the first tradable price after the news, hold 21 sessions.
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
fs = sorted(glob.glob(os.path.join(H, 'divs_*.csv')))
ev = pd.concat([pd.read_csv(f, dtype=str) for f in fs], ignore_index=True)
ev['date'] = pd.to_datetime(ev['date'], errors='coerce'); ev = ev.dropna(subset=['date'])
ev['ticker'] = ev.ticker.str.strip().str.upper()
for c in ('dps_proposed', 'dps_prev'): ev[c] = pd.to_numeric(ev[c], errors='coerce')
ev = ev.dropna(subset=['dps_proposed', 'dps_prev'])
ev['note'] = ev.note.fillna(''); ev['with_results'] = ev.with_results.fillna('unknown').str.strip().str.lower()
ev = ev.drop_duplicates(['ticker', 'fiscal_year']).sort_values('date')
def kind(a, b):
    if b == 0 and a == 0: return 'none_again'
    if b == 0: return 'first'
    if a == 0: return 'skipped'
    ch = a / b - 1
    return 'raise20' if ch >= 0.2 else ('cut20' if ch <= -0.2 else 'flat')
ev['kind'] = [kind(a, b) for a, b in zip(ev.dps_proposed, ev.dps_prev)]
ev['chg'] = np.where(ev.dps_prev > 0, (ev.dps_proposed / ev.dps_prev - 1) * 100, np.nan)
print('events', len(ev), '| with prices', ev.ticker.isin(AD.columns).sum(), '| kinds', ev.kind.value_counts().to_dict())

rows = []
for _, e in ev.iterrows():
    t = e.ticker
    if t not in AD.columns: continue
    d = e.date; tm = str(e.session_timing).strip().lower()
    i = idx.searchsorted(d)
    if i >= len(idx) or i < 22: continue
    if idx[i] != d: tm = 'before'
    if tm == 'before':   ie, px = i, AOP[t].iloc[i]
    elif tm == 'during': ie, px = i, AD[t].iloc[i]
    elif tm == 'after':  ie, px = i + 1, AOP[t].iloc[i + 1] if i + 1 < len(idx) else np.nan
    else:                ie, px = i + 1, AD[t].iloc[i + 1] if i + 1 < len(idx) else np.nan
    ix = ie + HOLD
    if ix >= len(idx) or not np.isfinite(px) or not np.isfinite(AD[t].iloc[ix]): continue
    pb = AD[t].iloc[i - 1]
    react = (px / pb - 1) * 100 - (W.iloc[ie] / W.iloc[i - 1] - 1) * 100 if np.isfinite(pb) else np.nan
    gross = (AD[t].iloc[ix] / px - 1) * 100          # adj_close -> includes the dividend if ex-date falls in the window
    r = gross - cst(t, ie)
    b = bench(ie - 1 if tm in ('before', 'after') else ie, ix)
    sh = -gross - (0.6 + cst(t, ie) - 0.78 + 0.7 * HOLD / 252)
    yld = e.dps_proposed / CL[t].iloc[i - 1] * 100 if np.isfinite(CL[t].iloc[i - 1]) else np.nan
    if t not in RAND: RAND[t] = own_rand(t)
    rows.append(dict(t=t, d=idx[ie], fy=e.fiscal_year, kind=e.kind, chg=e.chg, yld=yld, wr=e.with_results, tm=tm, react=react,
                     r=r, x=r - b, sh=sh, ctl=RAND[t], turn=TURN[t].iloc[ie], note=e.note[:40]))
df = pd.DataFrame(rows)
df.to_csv(os.path.join(H, f'r24a_trades_h{HOLD}.csv'), index=False)

def rep(g, lab):
    if len(g) < 4: print(f"{lab:46s} n={len(g)}"); return
    y = g.d.dt.year; tt = g.x.mean() / g.x.std() * np.sqrt(len(g))
    print(f"{lab:46s} n={len(g):3d} net {g.r.mean():+5.2f}% | vs ETF {g.x.mean():+5.2f}pp med {g.x.median():+5.2f} t {tt:4.1f} "
          f"beats {100*(g.x>0).mean():3.0f}% | <2020 {g.x[y<2020].mean():+5.2f} (n={int((y<2020).sum())}) 2020+ {g.x[y>=2020].mean():+5.2f} "
          f"| excess {g.x.mean()-g.ctl.mean():+5.2f} | react {g.react.mean():+4.1f} | XTB short {g.sh.mean():+5.2f}% win {100*(g.sh>0).mean():3.0f}%")

print(f'\n== first tradable price after the board proposal, hold {HOLD}')
rep(df, 'all proposals')
for k in ('raise20', 'flat', 'cut20', 'first', 'skipped', 'none_again'): rep(df[df.kind == k], '  ' + k)
up = df[df.kind.isin(['raise20', 'first'])]; dn = df[df.kind.isin(['cut20', 'skipped'])]
rep(up, 'positive surprise (raise >= 20% or first)'); rep(up[up.wr != 'yes'], '   not with results'); rep(up[up.wr == 'yes'], '   with results')
rep(up[up.turn > 3e6], '   liquid'); rep(up[up.react < 2], '   reaction < +2%'); rep(up[up.react >= 2], '   reaction >= +2%')
rep(df[df.chg >= 50], 'raise >= 50%')
rep(dn, 'negative surprise (cut >= 20% or skipped)'); rep(dn[dn.wr != 'yes'], '   not with results'); rep(dn[dn.turn > 3e6], '   liquid')
rep(df[df.yld >= 8], 'proposed yield >= 8%'); rep(df[(df.yld >= 5) & (df.yld < 8)], 'yield 5-8%'); rep(df[df.yld < 5], 'yield < 5%')
print('\nper-ticker:', df.t.value_counts().to_dict())
