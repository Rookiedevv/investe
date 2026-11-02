# Orlen diesel-crack paper-trade signal (round 26). Run after the research-prices workflow has refreshed research/prices*.
# Signal for month M: diesel crack (HO=F*42 - BZ=F, USD/bbl) change over the 21 sessions to the day BEFORE the last Warsaw
# session of month M-1. >= +5 -> buy PKN at the close of the first Warsaw session of month M, sell at the close of the 21st session
# after entry. <= -5 -> avoid Orlen longs that month. Prints the signal, the entry and the exit dates/prices that are already known.
import pandas as pd, numpy as np, pathlib, sys
R = pathlib.Path(__file__).resolve().parents[2]
def ld(p):
    d = pd.read_csv(p, parse_dates=['date']).set_index('date'); return d[~d.index.duplicated()].sort_index()
W = ld(R / 'data/prices/WIG20.csv'); idx = W.index[W.index >= '2014-01-01']
pkn = ld(R / 'research/prices/PKN.csv')['close'].reindex(idx)
ho = ld(R / 'research/prices_foreign/HO=F.csv')['adj_close'].reindex(idx).ffill(limit=5)
bz = ld(R / 'research/prices_foreign/BZ=F.csv')['adj_close'].reindex(idx).ffill(limit=5)
crack = ho * 42 - bz
month = pd.Period(sys.argv[1], 'M') if len(sys.argv) > 1 else pd.Timestamp.today().to_period('M')
prev = idx[idx.to_period('M') == month - 1]
if len(prev) < 2: sys.exit(f'no sessions for {month - 1}')
a = idx.get_loc(prev[-1]); s0 = a - 1
sig = crack.iloc[s0] - crack.iloc[s0 - 21]
print(f'month {month}: diesel crack {crack.iloc[s0]:.1f} USD/bbl on {idx[s0]:%Y-%m-%d}, 21-session change {sig:+.1f} -> '
      + ('BUY PKN' if sig >= 5 else ('AVOID Orlen longs' if sig <= -5 else 'no signal')))
cur = idx[idx.to_period('M') == month]
if len(cur):
    e = idx.get_loc(cur[0]); print(f'entry session {idx[e]:%Y-%m-%d} PKN close {pkn.iloc[e]:.2f}' if np.isfinite(pkn.iloc[e]) else f'entry session {idx[e]:%Y-%m-%d} close not available yet')
    print(f'exit = close of 21st session after entry (expected around {(idx[e] + pd.tseries.offsets.BDay(21)):%Y-%m-%d})')
else:
    print('first session of the month has no data yet')
