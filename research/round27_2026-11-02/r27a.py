# Round 27a: periodic-report date changes (postponed / brought forward) on GPW -> buy at the first tradable price after the news, hold 21 sessions.
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
fs = sorted(glob.glob(os.path.join(H, 'dates_*.csv')))
ev = pd.concat([pd.read_csv(f, dtype=str) for f in fs], ignore_index=True)
for c in ('date', 'old_date', 'new_date'): ev[c] = pd.to_datetime(ev[c], errors='coerce')
ev = ev.dropna(subset=['date'])
ev['ticker'] = ev.ticker.str.strip().str.upper()
for c in ('direction', 'reason', 'note'): ev[c] = ev[c].fillna('').str.strip().str.lower()
ev['covid'] = ev.note.str.contains('covid') | ((ev.date >= '2020-03-10') & (ev.date <= '2020-06-30'))
ev['shift'] = (ev.new_date - ev.old_date).dt.days
ev = ev.drop_duplicates(['date', 'ticker', 'report']).sort_values('date')
print('events', len(ev), '| with prices', ev.ticker.isin(AD.columns).sum(), '| dir', ev.direction.value_counts().to_dict(), '| covid', int(ev.covid.sum()))

rows = []
for _, e in ev.iterrows():
    t = e.ticker
    if t not in AD.columns: continue
    d = e.date; tm = str(e.session_timing).strip().lower()
    i = idx.searchsorted(d)
    if i >= len(idx) or i < 2: continue
    if idx[i] != d: tm = 'before'
    if tm == 'before':   ie, px = i, AOP[t].iloc[i]
    elif tm == 'during': ie, px = i, AD[t].iloc[i]
    elif tm == 'after':  ie, px = i + 1, AOP[t].iloc[i + 1] if i + 1 < len(idx) else np.nan
    else:                ie, px = i + 1, AD[t].iloc[i + 1] if i + 1 < len(idx) else np.nan
    ix = ie + HOLD
    if ix >= len(idx) or not np.isfinite(px) or not np.isfinite(AD[t].iloc[ix]): continue
    pb = AD[t].iloc[i - 1]
    react = (px / pb - 1) * 100 - (W.iloc[ie] / W.iloc[i - 1] - 1) * 100 if np.isfinite(pb) else np.nan
    gross = (AD[t].iloc[ix] / px - 1) * 100
    r = gross - cst(t, ie); b = bench(ie - 1 if tm in ('before', 'after') else ie, ix)
    sh = -gross - (0.6 + cst(t, ie) - 0.78 + 0.7 * HOLD / 252)
    # report-day window: close before the (new) report date -> close of the session after it (covers before/after-session filings)
    rep = to_rep = np.nan
    if pd.notna(e.new_date):
        j = idx.searchsorted(e.new_date)
        if 1 <= j < len(idx) - 1 and j > ie:
            a0, a1 = AD[t].iloc[j - 1], AD[t].iloc[j + 1]
            if np.isfinite(a0) and np.isfinite(a1): rep = (a1 / a0 - 1) * 100 - (W.iloc[j + 1] / W.iloc[j - 1] - 1) * 100
            if np.isfinite(a0): to_rep = (a0 / px - 1) * 100 - (W.iloc[j - 1] / W.iloc[ie] - 1) * 100
    if t not in RAND: RAND[t] = own_rand(t)
    rows.append(dict(t=t, d=idx[ie], dirn=e.direction, covid=bool(e.covid), sh_days=e['shift'], reason=e.reason[:40], report=e.report, tm=tm,
                     react=react, r=r, x=r - b, sh=sh, ctl=RAND[t], turn=TURN[t].iloc[ie], rep=rep, to_rep=to_rep))
df = pd.DataFrame(rows)
df.to_csv(os.path.join(H, f'r27a_trades_h{HOLD}.csv'), index=False)

def rep_(g, lab):
    if len(g) < 4: print(f"{lab:46s} n={len(g)}"); return
    y = g.d.dt.year; tt = g.x.mean() / g.x.std() * np.sqrt(len(g))
    print(f"{lab:46s} n={len(g):3d} net {g.r.mean():+5.2f}% | vs ETF {g.x.mean():+5.2f}pp med {g.x.median():+5.2f} t {tt:4.1f} beats {100*(g.x>0).mean():3.0f}% "
          f"| <2021 {g.x[y<2021].mean():+5.2f} 2021+ {g.x[y>=2021].mean():+5.2f} | excess {g.x.mean()-g.ctl.mean():+5.2f} | react {g.react.mean():+4.1f} "
          f"| notice->report {g.to_rep.mean():+5.2f} (n={g.to_rep.notna().sum()}) report-day {g.rep.mean():+5.2f} neg {100*(g.rep<0).mean():3.0f}% | XTB short {g.sh.mean():+5.2f}% win {100*(g.sh>0).mean():3.0f}%")

print(f'\n== first tradable price after the notice, hold {HOLD} (vs WIG20 TR ETF); report-day = close before -> close after the new date, vs WIG20')
nc = df[~df.covid]
rep_(df, 'all'); rep_(df[df.covid], 'covid-period changes')
for dn in ('later', 'earlier'):
    g = nc[nc.dirn == dn]; rep_(g, f'{dn} (ex covid)')
    rep_(g[g.turn > 3e6], '   liquid'); rep_(g[g.turn <= 3e6], '   illiquid')
    if dn == 'later':
        rep_(g[g['sh_days'] >= 14], '   delay >= 14 days'); rep_(g[g['sh_days'] < 14], '   delay < 14 days')
        rep_(g[g.reason.str.contains('audit|biegł|badan|impair|odpis|test|aud')], '   reason audit/impairment')
        rep_(g[g.report.str.lower().str.contains('fy|roczn|annual')], '   annual report')
print('\nper-ticker:', df.t.value_counts().to_dict())
