"""Round 36: current growth + trend ranking of liquid GPW stocks.
Usage: INVESTE=<repo> python3 signal_now.py [YYYY-MM-DD]   (ranking at the close of the last session on or before that date; default = last complete session)
Prints the 5 best (paper-trade basket), the worst quintile (avoid list) and data-freshness warnings."""
import sys, os
if len(sys.argv) > 1: os.environ['ASOF'] = (__import__('pandas').Timestamp(sys.argv[1]) + __import__('pandas').Timedelta(days=1)).strftime('%Y-%m-%d')
from gm36 import *
i = len(idx) - 1
sc, C, S = score(i)
tv = TURN.iloc[i]; lastpx = CL.apply(lambda s: s.last_valid_index())
liq = [t for t in sc.dropna().index if np.isfinite(tv.get(t, np.nan)) and tv[t] >= 2e6 and (idx[i] - lastpx[t]).days <= 5]
r = sc.reindex(liq).sort_values(ascending=False)
out = pd.DataFrame({'score': r.round(3), 'turnover_m': (tv.reindex(r.index) / 1e6).round(1), 'close': CL.ffill(limit=5).iloc[i].reindex(r.index),
                    'last_quarter': S.period.reindex(r.index), 'published': pd.to_datetime(S.avail.reindex(r.index)).dt.date,
                    'd_ni_%eq': (C['d_ni'].reindex(r.index) * 100).round(1), 'sue': C['sue'].reindex(r.index).astype(float).round(2),
                    'mom12_1/vol': C['mom12_1/vol'].reindex(r.index).round(1), 'vs_52w_high': C['near 52w high'].reindex(r.index).round(3)})
out['cost_%'] = np.select([out.turnover_m > 30, out.turnover_m > 10, out.turnover_m > 3], [0.9, 1.0, 1.3], 2.0)
print('ranking day:', idx[i].date(), '| liquid stocks ranked:', len(r), '| WIG proxy level', round(WIG.iloc[i], 2))
stale = sorted(set(TICK) - set(lastpx[lastpx >= idx[i] - pd.Timedelta(days=5)].index))
log = R + '/research/fundamentals/raw/_fetch_log.txt'
print('statements last fetched:', [l for l in open(log) if l.startswith('fetched')][-1].strip() if os.path.exists(log) else 'unknown')
if stale: print('WARNING prices older than 5 days for', len(stale), 'tickers:', ' '.join(stale[:40]))
nq = [t for t in tv[tv >= 2e6].index if t not in liq]
if nq: print('liquid but not ranked (no fresh report, short history or stale price):', ' '.join(nq))
k = max(3, int(round(len(r) * 0.2)))
print('\nTOP 5 (paper-trade basket)'); print(out.head(5).to_string())
print('\nnext 5 (reserves)'); print(out.iloc[5:10].to_string())
print(f'\nWORST QUINTILE ({k} stocks) - avoid list'); print(out.tail(k).to_string())
out.to_csv('ranking_%s.csv' % idx[i].date())
