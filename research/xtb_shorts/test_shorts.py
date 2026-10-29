"""XTB-short tests of the project's existing avoid signals (29 Oct 2026).

Each avoid signal (a stock that tends to lag after an event) is turned into a short:
short at the first tradable close after the event, cover after HOLD sessions.
Net of XTB costs: 0.30% markup each way + per-stock spread and price impact
(claude/stock_costs.csv tiers) + short swap (~0.7%/yr). Benchmark WIG20.
Placebo: random entry days in the same stock, same hold. Non-overlapping per stock.
"""
import math
import random
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import events as E  # noqa: E402

HOLD = 21
TODAY = "2026-10-29"
SPREAD_IMPACT = {  # spread + impact from claude/stock_costs.csv (eMakler commission removed)
    "PXM": 0.62, "EUR": 1.88, "DNP": 0.18, "PCO": 0.24, "CDR": 0.20, "11B": 1.61, "TEN": 1.67,
    "CIG": 1.52, "PLW": 2.22, "RBW": 0.90, "LPP": 0.20, "ALE": 0.17, "JSW": 0.34, "LWB": 1.51,
    "PKN": 0.16, "KGH": 0.10,
}


def xtb_cost(t, turnover_m=None):
    si = SPREAD_IMPACT.get(t)
    if si is None:
        T = max(turnover_m or 1.0, 0.05)
        spread = 0.1 if T > 30 else 0.2 if T > 10 else 0.5 if T > 3 else 0.8 if T > 1 else 1.0
        si = spread + 0.08 * math.sqrt(100 / T)
    return 0.60 + si + 0.7 * HOLD / 252


def load(t):
    p = ROOT / "research" / "prices" / f"{t}.csv"
    if not p.exists():
        p = ROOT / "data" / "prices" / f"{t}.csv"
    if not p.exists():
        return None
    d = pd.read_csv(p)
    d = d[d.date < TODAY]
    s = d.set_index("date")
    return s


W = load("WIG20")["close"]


def turnover(t):
    s = load(t)
    x = (s["close"] * s["volume"]).iloc[-250:]
    return x.median() / 1e6


class Stock:
    def __init__(self, t):
        s = load(t)
        self.t = t
        df = pd.DataFrame({"p": s["adj_close"], "c": s["close"]}).join(W.rename("w"), how="inner").dropna()
        self.df = df
        self.dates = list(df.index)
        self.cost = xtb_cost(t, turnover(t))
        r = df["p"].pct_change()
        rw = df["w"].pct_change()
        self.rel = (r - rw) * 100

    def idx(self, date, timing):
        """Index of the first close at which news on `date` with `timing` is tradable."""
        i = next((k for k, d in enumerate(self.dates) if d >= date), None)
        if i is None:
            return None
        if self.dates[i] == date and timing in ("after", "unknown"):
            i += 1
        return i if i < len(self.dates) else None

    def short(self, i, hold=HOLD):
        if i is None or i + hold >= len(self.dates):
            return None
        p0, p1 = self.df["p"].iloc[i], self.df["p"].iloc[i + hold]
        w0, w1 = self.df["w"].iloc[i], self.df["w"].iloc[i + hold]
        stock = (p1 / p0 - 1) * 100
        return dict(t=self.t, date=self.dates[i], stock=stock, vs_w20=stock - (w1 / w0 - 1) * 100,
                    net=-stock - self.cost)

    def placebo(self, n=2000, hold=HOLD, start="2018-01-01", seed=1):
        rnd = random.Random(seed)
        ks = [k for k, d in enumerate(self.dates) if d >= start and k + hold < len(self.dates)]
        out = [self.short(rnd.choice(ks), hold)["net"] for _ in range(n)]
        return sum(out) / len(out)


def nonoverlap(trades, hold=HOLD):
    trades = sorted(trades, key=lambda x: (x["t"], x["date"]))
    keep, last = [], {}
    for tr in trades:
        k = tr["t"]
        if k in last and tr["_i"] - last[k] < hold:
            continue
        keep.append(tr)
        last[k] = tr["_i"]
    return keep


def summary(name, trades, placebo=None, split="2022-01-01"):
    if not trades:
        print(f"{name}: no trades")
        return
    df = pd.DataFrame(trades)
    n = len(df)
    m = df.net.mean()
    sd = df.net.std(ddof=1) if n > 1 else float("nan")
    t = m / (sd / math.sqrt(n)) if n > 1 and sd > 0 else float("nan")
    a = df[df.date < split].net
    b = df[df.date >= split].net
    print(f"{name}: n={n} net {m:+.1f}% median {df.net.median():+.1f}% wins {100*(df.net>0).mean():.0f}% "
          f"t {t:.1f} | stock vs WIG20 {df.vs_w20.mean():+.1f} pp | <2022 {a.mean():+.1f}% (n={len(a)}) "
          f"2022+ {b.mean():+.1f}% (n={len(b)}) | worst {df.net.min():+.1f}% best {df.net.max():+.1f}%"
          + (f" | random shorts {placebo:+.1f}%" if placebo is not None else ""))
    return df


def run_events(t, evs, cond=None, hold=HOLD):
    s = Stock(t)
    out = []
    for e in evs:
        date, timing = e[0], e[1]
        i = s.idx(date, timing)
        if i is None or i < 1:
            continue
        react = s.rel.iloc[i]
        if cond is not None and not cond(react, e):
            continue
        tr = s.short(i, hold)
        if tr:
            tr["_i"], tr["react"] = i, react
            out.append(tr)
    return nonoverlap(out, hold), s


def main():
    print("== H1 Polimex: short after a contract pop ==")
    for th in (3, 5):
        tr, s = run_events("PXM", E.PXM_CONTRACTS, lambda r, e, th=th: r >= th)
        summary(f"PXM contract, reaction >= +{th}% vs WIG20", tr, s.placebo())
    tr, s = run_events("PXM", E.PXM_CONTRACTS,
                       lambda r, e: e[2] >= 0.10 * E.PXM_PREV_REV[int(e[0][:4])])
    summary("PXM contract >= 10% of prev-year revenue (any reaction)", tr, s.placebo())
    tr, s = run_events("PXM", E.PXM_CONTRACTS,
                       lambda r, e: e[2] >= 0.10 * E.PXM_PREV_REV[int(e[0][:4])] and r >= 3)
    summary("PXM contract >= 10% revenue AND reaction >= +3%", tr, s.placebo())

    print("\n== H2 Eurocash: short after a bad own report / bad Dino report ==")
    for th in (-3, -5):
        tr, s = run_events("EUR", E.EUR_REPORTS, lambda r, e, th=th: r <= th)
        summary(f"EUR own report, reaction <= {th}%", tr, s.placebo())
    tr, s = run_events("EUR", E.EUR_REPORTS, None)
    summary("EUR any report", tr, s.placebo())
    d = Stock("DNP")
    eur = Stock("EUR")
    out = []
    for date, timing in E.DNP_REPORTS:
        i = d.idx(date, timing)
        if i is None or d.rel.iloc[i] > -3:
            continue
        j = eur.idx(d.dates[i], "before")
        tr = eur.short(j)
        if tr:
            tr["_i"] = j
            out.append(tr)
    summary("EUR after Dino reaction <= -3%", nonoverlap(out), eur.placebo())

    print("\n== H3 Pepco: short after a bad Inditex/H&M day ==")
    p = Stock("PCO")
    for th in (-3, -5):
        for lag, lab in ((0, "same-day close"), (1, "next close")):
            out = []
            for date, r in E.PEER_DAYS:
                if r > th:
                    continue
                i = p.idx(date, "before")
                if i is None:
                    continue
                i += lag
                tr = p.short(i)
                if tr:
                    tr["_i"] = i
                    out.append(tr)
            summary(f"PCO after peer day <= {th}% ({lab})", nonoverlap(out), p.placebo(start="2021-06-01"))
    for t in ("LPP",):
        q = Stock(t)
        out = []
        for date, r in E.PEER_DAYS:
            if r > -3:
                continue
            i = q.idx(date, "before")
            tr = q.short(i) if i is not None else None
            if tr:
                tr["_i"] = i
                out.append(tr)
        summary(f"{t} after peer day <= -3% (control)", nonoverlap(out), q.placebo(start="2021-06-01"))

    print("\n== H4 Gaming: short the month after a launch ==")
    rows = []
    for date, t, timing, lab in E.LAUNCHES:
        if "excluded" in lab:
            continue
        s = Stock(t)
        i = s.idx(date, timing)
        tr = s.short(i) if i is not None else None
        if tr:
            tr["_i"], tr["react"], tr["lab"] = i, s.rel.iloc[i], lab
            rows.append(tr)
    rows = nonoverlap(rows)
    summary("All launches", rows)
    summary("Launches 2021+", [r for r in rows if r["date"] >= "2021-01-01"])
    summary("Launches 2021+, launch day >= +3%", [r for r in rows if r["date"] >= "2021-01-01" and r["react"] >= 3])
    summary("Liquid only (CDR, 11B), all years", [r for r in rows if r["t"] in ("CDR", "11B")])
    for r in sorted(rows, key=lambda x: x["date"]):
        print(f"   {r['date']} {r['t']:4} {r['lab'][:28]:28} day {r['react']:+5.1f}%  next 21 stock {r['stock']:+6.1f}%  short net {r['net']:+6.1f}%")

    print("\n== H5 Index revisions (WIG20 / mWIG40): short demotions / promotions ==")
    ic = pd.read_csv(ROOT / "research" / "xtb_shorts" / "index_changes.csv")
    ic = ic.dropna(subset=["announce_date", "effective_date"])
    rank = {"WIG20": 3, "mWIG40": 2, "sWIG80": 1}
    up, down = [], []
    for r in ic.itertuples():
        if r.index not in ("WIG20", "mWIG40"):
            continue
        fr = rank.get(r.from_index if isinstance(r.from_index, str) else "", 0)
        to = rank.get(r.to_index if isinstance(r.to_index, str) else "", 0)
        if r.change == "add" and to > fr:
            up.append(r)
        if r.change == "remove" and to < fr:
            down.append(r)
    res = {"demote_ann_to_eff": [], "promote_after_eff": [], "demote_after_eff": [], "promote_ann_to_eff": []}
    cache = {}
    for kind, lst in (("demote", down), ("promote", up)):
        for r in lst:
            t = r.ticker
            if t not in cache:
                cache[t] = Stock(t) if load(t) is not None else None
            s = cache[t]
            if s is None:
                continue
            ia = s.idx(r.announce_date, "after")      # announcements come after the session
            ie = s.idx(r.effective_date, "before")    # first session in the new index
            if ia is None or ie is None or ie <= ia:
                continue
            h = ie - 1 - ia                           # cover at the rebalancing close
            if h >= 1:
                tr = s.short(ia, h)
                if tr:
                    tr["net"] = -tr["stock"] - (s.cost - 0.7 * HOLD / 252 + 0.7 * h / 252)
                    tr["_i"] = ia
                    res[f"{kind}_ann_to_eff"].append(tr)
            tr = s.short(ie - 1)                       # short at the rebalancing close, hold 21
            if tr:
                tr["_i"] = ie - 1
                res[f"{kind}_after_eff"].append(tr)
    for k, v in res.items():
        summary(k, v)
    pr = pd.DataFrame(res["promote_after_eff"])
    if len(pr):
        print("   promotions, by stock turnover today:")
        pr["turn"] = [turnover(t) for t in pr.t]
        summary("   promote_after_eff, turnover >= 3m zł", pr[pr.turn >= 3].to_dict("records"))

    print("\n== H6 Big down day (>2.5 SD below WIG20) -> short 21 sessions, beyond JSW ==")
    allt = sorted({p.stem for p in (ROOT / "research" / "prices").glob("*.csv") if not p.stem.startswith("_")})
    rows = []
    for t in allt:
        s = Stock(t)
        if turnover(t) < 3 or len(s.dates) < 600:
            continue
        sd = s.rel.rolling(250).std().shift(1)
        hits = [k for k in range(260, len(s.dates)) if s.rel.iloc[k] < -2.5 * sd.iloc[k] and s.dates[k] >= "2018-01-01"]
        tr = [dict(s.short(k), _i=k) for k in hits if s.short(k)]
        tr = nonoverlap(tr)
        if tr:
            m = sum(x["net"] for x in tr) / len(tr)
            rows.extend(tr)
            print(f"   {t:4} n={len(tr):3} short net {m:+5.1f}%  wins {100*sum(x['net']>0 for x in tr)/len(tr):3.0f}%")
    summary("All liquid names (turnover >= 3m zł), excl. JSW", [r for r in rows if r["t"] != "JSW"])
    summary("RBW only", [r for r in rows if r["t"] == "RBW"])


if __name__ == "__main__":
    main()
