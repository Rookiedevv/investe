"""Build the decision-time feature table for the WIG20 dip model.

Decision is made after the US close on day t (≈22:00 Warsaw); the trade is opened at the
Warsaw open on the next session t+1. So every feature on row t uses only data with
date <= t for Warsaw/European/FX series and US series (US day t closes after Warsaw day t,
but before Warsaw day t+1 opens). Targets look forward from the open of t+1.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

PRICES = "data/prices"


def load(ticker: str) -> pd.DataFrame:
    df = pd.read_csv(f"{PRICES}/{ticker}.csv", parse_dates=["date"]).set_index("date").sort_index()
    df = df[~df.index.duplicated(keep="last")]
    return df


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def build(base: str = "ETFBW20TR") -> pd.DataFrame:
    w = load(base)
    c, o, h, l, v = w["close"], w["open"], w["high"], w["low"], w["volume"].astype(float)
    f = pd.DataFrame(index=w.index)
    r = np.log(c).diff()
    f["r1"] = r
    for k in (2, 3, 5, 10, 20, 60):
        f[f"r{k}"] = np.log(c).diff(k)
    f["vol10"] = r.rolling(10).std()
    f["vol20"] = r.rolling(20).std()
    f["vol60"] = r.rolling(60).std()
    f["volratio"] = f["vol10"] / f["vol60"]
    f["range"] = (h - l) / c
    f["range_rel"] = f["range"] / f["range"].rolling(20).mean()
    f["gap"] = np.log(o / c.shift(1))
    f["clv"] = ((c - l) / (h - l).replace(0, np.nan)).fillna(0.5)  # close location in day's range
    f["oc"] = np.log(c / o)  # intraday move
    for n in (20, 60, 250):
        f[f"dd{n}"] = c / c.rolling(n).max() - 1  # distance below rolling high
        f[f"up{n}"] = c / c.rolling(n).min() - 1
    f["ma20"] = c / c.rolling(20).mean() - 1
    f["ma50"] = c / c.rolling(50).mean() - 1
    f["ma200"] = c / c.rolling(200).mean() - 1
    f["rsi14"] = rsi(c, 14)
    f["rsi3"] = rsi(c, 3)
    f["days_since_high20"] = (c.rolling(20).apply(lambda x: len(x) - 1 - int(np.argmax(x)), raw=True))
    f["updays5"] = (r > 0).rolling(5).sum()
    f["streak"] = _streak(r)
    f["volu_ratio"] = v / v.rolling(20).mean().replace(0, np.nan)
    f["zscore20"] = (c - c.rolling(20).mean()) / c.rolling(20).std()

    # Foreign series: value on the same calendar date t (US closes after Warsaw but before t+1 open).
    for tk in ("SPX", "NDQ", "DAX", "VIX", "BRENT", "EURPLN", "USDPLN"):
        try:
            s = load(tk)["close"]
        except FileNotFoundError:
            continue
        s = s.reindex(s.index.union(w.index)).ffill().reindex(w.index)
        if tk == "VIX":
            f["vix"] = s
            f["vix_chg1"] = np.log(s).diff()
            f["vix_chg5"] = np.log(s).diff(5)
            f["vix_z"] = (s - s.rolling(60).mean()) / s.rolling(60).std()
        else:
            ls = np.log(s)
            f[f"{tk.lower()}_r1"] = ls.diff()
            f[f"{tk.lower()}_r5"] = ls.diff(5)
            f[f"{tk.lower()}_r20"] = ls.diff(20)
    if "spx_r1" in f:
        f["spx_minus_wig_r5"] = f["spx_r5"] - f["r5"]

    # Calendar (known in advance)
    idx = w.index
    f["dow"] = idx.dayofweek
    f["month"] = idx.month
    nxt = pd.Series(idx, index=idx).shift(-1)  # next session date
    f["next_is_monday"] = (nxt.dt.dayofweek == 0).astype(float)
    f["turn_of_month"] = ((idx.day >= 27) | (idx.day <= 3)).astype(float)
    f["expiry_week"] = ((idx.day >= 15) & (idx.day <= 21)).astype(float)  # 3rd-Friday week

    # Targets: forward from next session's open
    o1 = o.shift(-1)
    f["t_oc1"] = np.log(c.shift(-1) / o1)                 # next day open->close
    f["t_cc1"] = np.log(c.shift(-1) / c)                   # next day close->close
    for k in (2, 3, 5):
        f[f"t_oc{k}"] = np.log(c.shift(-k) / o1)           # open t+1 -> close t+k
    f["t_minlow3"] = np.log(l.shift(-3).rolling(3).min().shift(0) / o1)  # placeholder, refined below
    lows = pd.concat([l.shift(-k) for k in (1, 2, 3)], axis=1).min(axis=1)
    f["t_minlow3"] = np.log(lows / o1)                     # best reachable short P&L within 3 days
    f["next_open"] = o1
    f["next_close"] = c.shift(-1)
    f["close"] = c
    return f


def _streak(r: pd.Series) -> pd.Series:
    out = np.zeros(len(r))
    s = 0
    for i, x in enumerate(r.values):
        if np.isnan(x):
            s = 0
        elif x > 0:
            s = s + 1 if s > 0 else 1
        elif x < 0:
            s = s - 1 if s < 0 else -1
        else:
            s = 0
        out[i] = s
    return pd.Series(out, index=r.index)


FEATURES_WIG = ["r1", "r2", "r3", "r5", "r10", "r20", "r60", "vol10", "vol20", "vol60", "volratio", "range",
                "range_rel", "gap", "clv", "oc", "dd20", "dd60", "dd250", "up20", "up60", "up250", "ma20", "ma50",
                "ma200", "rsi14", "rsi3", "days_since_high20", "updays5", "streak", "volu_ratio", "zscore20",
                "dow", "month", "next_is_monday", "turn_of_month", "expiry_week"]
FEATURES_FOREIGN = ["spx_r1", "spx_r5", "spx_r20", "ndq_r1", "ndq_r5", "dax_r1", "dax_r5", "dax_r20", "vix", "vix_chg1",
                    "vix_chg5", "vix_z", "brent_r1", "brent_r5", "eurpln_r1", "eurpln_r5", "usdpln_r1", "usdpln_r5",
                    "spx_minus_wig_r5"]


if __name__ == "__main__":
    f = build()
    print(f.shape)
    print(f.dropna(subset=["t_oc1"]).tail())
