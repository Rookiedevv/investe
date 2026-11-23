"""Round 36: the growth + trend composite ("G+M") - one definition used by the backtest and by signal_now.py.

Score = average percentile rank (need at least 3 of 4) of
  d_ni            latest published quarter's net profit minus the same quarter a year earlier, divided by equity a year earlier
  sue             the same change divided by the standard deviation of the previous 8 such changes
  mom12_1/vol     return from 12 months ago to 1 month ago, divided by daily volatility over 250 sessions
  near 52w high   close / highest close of the last 252 sessions (dividend-adjusted)
Statements count only if the periodic report was published before the ranking day and at most 150 days ago.
"""
from lib36 import *
import fund36 as F

def components(i):
    S = F.snapshot(i)
    X = RET.iloc[i - 249:i + 1]; sd = X.std().where(X.notna().sum() >= 175)
    c = {'d_ni': S['d_ni'].astype(float) if len(S) else pd.Series(dtype=float), 'sue': S['sue'].astype(float) if len(S) else pd.Series(dtype=float),
         'mom12_1/vol': (AD.iloc[i - 21] / AD.iloc[i - 252] - 1) / sd, 'near 52w high': AD.ffill(limit=5).iloc[i] / AD.iloc[i - 251:i + 1].max()}
    return pd.DataFrame(c).replace([np.inf, -np.inf], np.nan), S

def score(i):
    C, S = components(i)
    Rk = C.rank(pct=True); n = Rk.notna().sum(axis=1)
    return (Rk.mean(axis=1)).where(n >= 3), C, S
