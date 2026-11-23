"""Round 36 helpers: price panel, WIG total-return proxy, costs, monthly factor evaluator."""
import glob, os, warnings
import numpy as np, pandas as pd
warnings.filterwarnings('ignore')
R = os.environ.get('INVESTE') or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
NON = {'WIG', 'WIG20', 'FW20', 'SPX', 'DAX', 'NDQ', 'VIX', 'EURPLN', 'USDPLN', 'BRENT', 'ETFBW20TR', 'HO', 'ETFW20L'}

def _load():
    P = {}
    for f in glob.glob(R + '/research/prices/*.csv') + glob.glob(R + '/data/prices/*.csv'):
        t = os.path.basename(f)[:-4]
        if t.startswith('_') or t in NON: continue
        d = pd.read_csv(f, parse_dates=['date']).dropna(subset=['close']).set_index('date')
        d = d[~d.index.duplicated()]; d = d[d['close'] > 0]
        if t in P and len(P[t]) > len(d): continue
        P[t] = d
    return P
P = _load(); TICK = sorted(P)
W20 = pd.read_csv(R + '/data/prices/WIG20.csv', parse_dates=['date']).set_index('date')['close']
seed = pd.read_csv(R + '/data/prices/seed/WIG20.csv', parse_dates=['Data']).set_index('Data')['Zamkniecie']
W20 = pd.concat([seed[seed.index < W20.index[0]], W20]).sort_index(); W20 = W20[~W20.index.duplicated()]
# trading calendar: WIG20 dates, extended by any later dates on which >= 20 stocks traded
alld = pd.concat([P[t]['close'].rename(t) for t in TICK], axis=1)
volp = pd.concat([P[t]['volume'].rename(t) for t in TICK], axis=1)
extra = volp.index[((volp > 0).sum(axis=1) >= 20) & (volp.index > W20.index[-1])]
cal = W20.index.union(extra)
TODAY = pd.Timestamp(os.environ.get('ASOF', pd.Timestamp.now(tz='Europe/Warsaw').strftime('%Y-%m-%d')))
idx = cal[(cal >= '2010-01-01') & (cal < TODAY)]   # drop today's partial bar
CL = pd.DataFrame({t: P[t]['close'] for t in TICK}).reindex(idx)
AD = pd.DataFrame({t: P[t]['adj_close'] for t in TICK}).reindex(idx)
VO = pd.DataFrame({t: P[t]['volume'] for t in TICK}).reindex(idx)
HI = pd.DataFrame({t: P[t]['high'] for t in TICK}).reindex(idx)
LO = pd.DataFrame({t: P[t]['low'] for t in TICK}).reindex(idx)
W20 = W20.reindex(idx).ffill()
TURN = (CL * VO).rolling(60, min_periods=20).median()
RET = AD.pct_change()
ind = pd.read_csv(R + '/research/round20_2026-10-30/indices_daily.csv', parse_dates=['date'])
ind = ind.pivot(index='date', columns='symbol', values='close').reindex(idx).ffill()
etf = pd.read_csv(R + '/data/prices/ETFBW20TR.csv', parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
r = W20.pct_change() + 0.035 / 252
rtr = ind['WIG20TR'].pct_change()
m = rtr.notna() & (idx > pd.Timestamp('2012-12-03')) & (idx <= pd.Timestamp('2026-01-02')); r[m] = rtr[m]
m26 = idx > pd.Timestamp('2026-01-02'); r[m26] = etf.pct_change()[m26]
W20TR = (1 + r.fillna(0)).cumprod() * 100
mix = 0.70 * ind['WIG20TR'].pct_change() + 0.22 * ind['MWIG40TR'].pct_change() + 0.08 * ind['SWIG80TR'].pct_change()
rw = r.copy(); mm = mix.notna() & (idx > pd.Timestamp('2017-09-21')) & (idx <= pd.Timestamp('2026-01-02')); rw[mm] = mix[mm]
WIG = (1 + rw.fillna(0)).cumprod() * 100
WRET = WIG.pct_change()
ETF_COST = 0.78

def cost_s(i):
    tv = TURN.iloc[i]
    c = pd.Series(np.select([tv > 30e6, tv > 10e6, tv > 3e6, tv > 1e6], [0.9, 1.0, 1.3, 2.0], 2.7), index=tv.index)
    return c

def month_ends(start='2015-06-01'):
    s = pd.Series(np.arange(len(idx)), index=idx)
    me = s.groupby([idx.year, idx.month]).last().values
    return [i for i in me if idx[i] >= pd.Timestamp(start)]

def fwd(i0, i1):
    """gross % return per stock from close i0 to close i1 (stocks that stop trading keep last price)"""
    a = AD.iloc[i0]; b = AD.ffill(limit=10).iloc[i1]
    return (b / a - 1) * 100

def wig(i0, i1): return (WIG.iloc[i1] / WIG.iloc[i0] - 1) * 100

def tstat(x):
    x = pd.Series(x).dropna()
    return x.mean() / x.std() * np.sqrt(len(x)) if len(x) > 2 and x.std() > 0 else np.nan
