"""The rules that survived the research, as code.

Every rule produces:
  - a backtest: the list of past trades it would have made (for the app's history and a sanity check);
  - a status for today: idle / watch / active / blocked, plus the numbers behind it.

Conventions (same as the research log):
  - returns use dividend-adjusted closes (adj_close) and the matching adjusted open;
  - cost 1% per round trip (eMakler 0.39% x 2 + spread);
  - "normal daily move" = mean absolute daily return over the previous 60 sessions.
"""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass, field, asdict

import pandas as pd

COST = 0.01
BANKS = ["PKO", "PEO", "EBP", "MBK", "ING", "MIL", "ALR", "BHW", "BNP"]
VOLATILE_BANKS = ["MIL", "MBK", "ALR"]
STATE_UTILS = ["PGE", "TPE", "ENA"]
CARPARTS = ["CAR", "APR"]


# ───────────────────────── Price helpers ─────────────────────────

def load_prices(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Wide adjusted close and adjusted open tables (index = session date)."""
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    factor = df["adj_close"] / df["close"]
    df["adj_open"] = df["open"] * factor
    close = df.pivot(index="date", columns="ticker", values="adj_close").sort_index()
    opn = df.pivot(index="date", columns="ticker", values="adj_open").sort_index()
    return close, opn


def basket(close: pd.DataFrame, tickers: list[str]) -> pd.Series:
    """Equal-weight daily-rebalanced basket index starting at 1."""
    r = close[tickers].pct_change().mean(axis=1, skipna=True).fillna(0)
    return (1 + r).cumprod()


def noise(series: pd.Series, window: int = 60) -> pd.Series:
    """Normal daily move known before each day (shifted so it uses only the past)."""
    return series.pct_change().abs().rolling(window, min_periods=20).mean().shift(1)


def session_index(sessions: pd.DatetimeIndex, day: pd.Timestamp) -> int:
    """Index of the first session on or after `day`."""
    return int(sessions.searchsorted(day))


def reaction_day(sessions: pd.DatetimeIndex, date: str, time: str | float | None, timing: str | None) -> int:
    """First session that could react: same day if released before/during the session, else the next one."""
    day = pd.Timestamp(date)
    i = session_index(sessions, day)
    after = False
    if isinstance(timing, str) and timing.startswith("after"):
        after = True
    elif isinstance(time, str) and time and time >= "17:00":
        after = True
    if after and i < len(sessions) and sessions[i] == day:
        i += 1
    return i


def shorten(text: str, n: int = 110) -> str:
    """Cut a description at a word boundary."""
    text = " ".join((text or "").split())
    if len(text) <= n:
        return text
    return text[:n].rsplit(" ", 1)[0].rstrip(",;:") + "…"


@dataclass
class Trade:
    rule: str
    ticker: str
    entry_date: str
    entry_price: float
    exit_date: str | None
    exit_price: float | None
    ret_net: float | None  # after costs; None while open
    reason: str = ""
    open: bool = False


def noise_exit(series: pd.Series, nz: pd.Series, start: int, k: float, max_days: int) -> tuple[int, bool]:
    """Sell at the close of the first day after `start` that falls more than k x normal move.
    Returns (exit index, still_open)."""
    last = len(series) - 1
    for j in range(start + 1, min(start + max_days, last) + 1):
        day_ret = series.iloc[j] / series.iloc[j - 1] - 1
        if not math.isnan(nz.iloc[j]) and day_ret < -k * nz.iloc[j]:
            return j, False
    end = start + max_days
    if end <= last:
        return end, False
    return last, True


# ───────────────────────── Rule 1: car-parts sales acceleration ─────────────────────────

def carparts_releases(sales: pd.DataFrame) -> pd.DataFrame:
    """Monthly sales releases with y/y growth and acceleration (y/y minus mean of the previous 3 months)."""
    s = sales[sales["period"].notna() & (sales["period"].astype(str) != "")].copy()
    s = s[s["ticker"].isin(CARPARTS)]
    s["sales_pln_m"] = pd.to_numeric(s["sales_pln_m"], errors="coerce")
    s["yoy_pct"] = pd.to_numeric(s["yoy_pct"], errors="coerce")
    s = s.sort_values(["ticker", "period"]).reset_index(drop=True)
    out = []
    for t, g in s.groupby("ticker"):
        g = g.copy()
        by_period = dict(zip(g["period"], g["sales_pln_m"]))
        def fill(row):
            if not math.isnan(row["yoy_pct"]):
                return row["yoy_pct"]
            y, m = row["period"].split("-")
            prev = by_period.get(f"{int(y) - 1}-{m}")
            if prev and not math.isnan(row["sales_pln_m"]):
                return round((row["sales_pln_m"] / prev - 1) * 100, 2)
            return float("nan")
        g["yoy_pct"] = g.apply(fill, axis=1)
        g["accel"] = g["yoy_pct"] - g["yoy_pct"].shift(1).rolling(3, min_periods=3).mean()
        out.append(g)
    return pd.concat(out).sort_values(["date", "time"]).reset_index(drop=True)


def rule_carparts(close: pd.DataFrame, opn: pd.DataFrame, releases: pd.DataFrame, threshold: float = 5.0):
    """Buy at the open 2 sessions after a release whose acceleration > threshold pp;
    sell at the open of the first session that can react to the next release."""
    sessions = close.index
    trades: list[Trade] = []
    for t in CARPARTS:
        g = releases[releases["ticker"] == t].reset_index(drop=True)
        for i, row in g.iterrows():
            if not (row["accel"] > threshold):
                continue
            d0 = reaction_day(sessions, row["date"], row["time"], row["session_timing"])
            e = d0 + 2
            if e >= len(sessions):
                continue  # entry day not reached yet; shown as a status instead
            entry = opn[t].iloc[e]
            if i + 1 < len(g):
                nxt = g.iloc[i + 1]
                x = reaction_day(sessions, nxt["date"], nxt["time"], nxt["session_timing"])
                if x < len(sessions):
                    ex = opn[t].iloc[x]
                    trades.append(Trade("carparts", t, sessions[e].date().isoformat(), round(entry, 2),
                                        sessions[x].date().isoformat(), round(ex, 2), ex / entry - 1 - COST,
                                        f"{row['period']}: +{row['accel']:.1f} pp"))
                    continue
            last = close[t].iloc[-1]
            trades.append(Trade("carparts", t, sessions[e].date().isoformat(), round(entry, 2), None, None,
                                None, f"{row['period']}: +{row['accel']:.1f} pp", open=True))
    return trades


def status_carparts(close: pd.DataFrame, releases: pd.DataFrame, trades: list[Trade], threshold: float = 5.0) -> dict:
    sessions = close.index
    per = []
    for t in CARPARTS:
        g = releases[releases["ticker"] == t]
        last = g.iloc[-1]
        open_trade = next((x for x in trades if x.ticker == t and x.open), None)
        item = {
            "ticker": t,
            "period": last["period"],
            "release_date": last["date"],
            "yoy": None if math.isnan(last["yoy_pct"]) else round(float(last["yoy_pct"]), 1),
            "accel": None if math.isnan(last["accel"]) else round(float(last["accel"]), 1),
            "signal": bool(last["accel"] > threshold),
        }
        if item["signal"]:
            d0 = reaction_day(sessions, last["date"], last["time"], last["session_timing"])
            if d0 + 2 < len(sessions):
                item["entry_date"] = sessions[d0 + 2].date().isoformat()
            else:
                item["entry_date"] = None  # buy at the open 2 sessions after the release
        if open_trade:
            item["entry_price"] = open_trade.entry_price
            item["last_close"] = round(float(close[t].iloc[-1]), 2)
            item["ret_now"] = item["last_close"] / open_trade.entry_price - 1 - COST
        # Next release expected about one month after the last one.
        item["next_release_est"] = (pd.Timestamp(last["date"]) + pd.DateOffset(months=1)).date().isoformat()
        per.append(item)
    state = "active" if any(p["signal"] for p in per) else "idle"
    return {"state": state, "threshold": threshold, "companies": per}


# ───────────────────────── Bank events: signs, seasons ─────────────────────────

def bank_event_sign(desc: str) -> int:
    d = (desc or "").lower()
    neg = "negative for banks" in d or "negative for dividends" in d or "negative for ch" in d or "strongly negative" in d
    pos = "positive for banks" in d or "positive (dividends" in d or "positive for ch" in d
    if neg and not pos:
        return -1
    if pos and not neg:
        return 1
    if "negative" in d and "positive" not in d:
        return -1
    if "positive" in d and "negative" not in d:
        return 1
    return 0


@dataclass
class Season:
    period: str
    early_tickers: list[str]
    release_date: str
    day0: str | None
    reaction: float | None  # early reporter(s) minus the other banks, day 0
    verdict: str  # good / bad / neutral / pending


def bank_seasons(events: pd.DataFrame, close: pd.DataFrame, today: pd.Timestamp) -> list[Season]:
    """First bank to report each results season and the market's day-0 reaction to it.
    If several banks report on the first day, their average is compared with the rest."""
    sessions = close.index
    r = close[BANKS].pct_change()
    res = events[(events["category"] == "bank_results") & events["period"].notna() & (events["period"] != "")].copy()
    # Annual reports follow the Q4 preliminary results, so they don't open a new season.
    res = res[~res["period"].str.endswith("FY")]
    res["key"] = res["date"] + " " + res["time"].fillna("12:00").replace("", "12:00")
    seasons = []
    for period, g in res.groupby("period"):
        g = g.sort_values("key")
        first_day = g.iloc[0]["date"]
        first = g[g["date"] == first_day]
        # Same day: if times are known, keep the earliest-released only when it is clearly first.
        early = list(dict.fromkeys(first["ticker"]))
        rel = first.iloc[0]
        d0 = reaction_day(sessions, rel["date"], rel["time"] if isinstance(rel["time"], str) else None,
                          rel["session_timing"])
        if pd.Timestamp(first_day) > today or d0 >= len(sessions):
            seasons.append(Season(period, early, first_day, None, None, "pending"))
            continue
        others = [b for b in BANKS if b not in early]
        react = float(r[early].iloc[d0].mean() - r[others].iloc[d0].mean())
        verdict = "good" if react >= 0.015 else "bad" if react <= -0.015 else "neutral"
        seasons.append(Season(period, early, first_day, sessions[d0].date().isoformat(), react, verdict))
    return sorted(seasons, key=lambda s: s.release_date)


# ───────────────────────── Rule 2: bank read-through ─────────────────────────

def rule_readthrough(close: pd.DataFrame, seasons: list[Season], k: float = 1.5, max_days: int = 20) -> list[Trade]:
    """After a good early report, buy the 9-bank basket at the close of day +1;
    sell at the close of the first day the basket falls more than k x its normal move (max 20 sessions)."""
    sessions = close.index
    b = basket(close, BANKS)
    nz = noise(b)
    trades = []
    for s in seasons:
        if s.verdict != "good":
            continue
        e = session_index(sessions, pd.Timestamp(s.day0)) + 1
        if e >= len(sessions):
            continue
        x, still_open = noise_exit(b, nz, e, k, max_days)
        ret = b.iloc[x] / b.iloc[e] - 1 - COST
        trades.append(Trade("readthrough", "BANKS", sessions[e].date().isoformat(), round(float(b.iloc[e]) * 100, 2),
                            None if still_open else sessions[x].date().isoformat(),
                            None if still_open else round(float(b.iloc[x]) * 100, 2),
                            None if still_open else ret, f"{s.period}: {'+'.join(s.early_tickers)} {s.reaction:+.1%}",
                            open=still_open))
    return trades


def status_readthrough(close: pd.DataFrame, seasons: list[Season], trades: list[Trade], events: pd.DataFrame,
                       today: pd.Timestamp) -> dict:
    sessions = close.index
    upcoming = [s for s in seasons if s.verdict == "pending"]
    done = [s for s in seasons if s.verdict != "pending"]
    last_done = done[-1] if done else None
    open_trade = next((t for t in trades if t.open), None)
    out = {
        "last_season": asdict(last_done) if last_done else None,
        "next_season": asdict(upcoming[0]) if upcoming else None,
        "open_trade": asdict(open_trade) if open_trade else None,
    }
    if upcoming:
        nxt = upcoming[0]
        sched = events[(events["category"] == "bank_results") & (events["period"] == nxt.period)]
        out["schedule"] = [{"ticker": r.ticker, "date": r.date} for r in sched.sort_values("date").itertuples()]
    if open_trade:
        out["state"] = "active"
        b = basket(close, BANKS)
        e = session_index(sessions, pd.Timestamp(open_trade.entry_date))
        out["ret_now"] = float(b.iloc[-1] / b.iloc[e] - 1 - COST)
        out["exit_drop"] = float(1.5 * noise(b).iloc[-1])
    elif upcoming and (pd.Timestamp(upcoming[0].release_date) - today).days <= 14:
        out["state"] = "watch"
    else:
        out["state"] = "idle"
    # A good early reaction in the last session: buy at today's close (day +1).
    if last_done and last_done.verdict == "good" and last_done.day0 == sessions[-1].date().isoformat():
        out["state"] = "active"
        out["buy_today"] = True
    return out


# ───────────────────────── Rule 3: bank regime (blackout after bad news) ─────────────────────────

def bank_bad_good_days(close: pd.DataFrame, events: pd.DataFrame, seasons: list[Season]):
    sessions = close.index
    bad, good = {}, {}
    shocks = events[(events["category"] == "sector_shock")]
    for r in shocks.itertuples():
        sign = bank_event_sign(r.description)
        if sign == 0:
            continue
        i = reaction_day(sessions, r.date, r.time if isinstance(r.time, str) else None, r.session_timing)
        if i >= len(sessions):
            continue
        (bad if sign < 0 else good)[i] = shorten(r.description)
    for s in seasons:
        if s.day0 and s.verdict in ("good", "bad"):
            i = session_index(sessions, pd.Timestamp(s.day0))
            (bad if s.verdict == "bad" else good)[i] = f"early report {s.period} ({'+'.join(s.early_tickers)} {s.reaction:+.1%})"
    b = basket(close, BANKS)
    two_day = b / b.shift(2) - 1
    for i in range(2, len(sessions)):
        if two_day.iloc[i] <= -0.06 and i not in bad:
            bad[i] = f"bank sell-off {two_day.iloc[i]:+.1%} in 2 days"
    return bad, good


def rule_regime(close: pd.DataFrame, bad: dict, good: dict, blackout: int = 20, window: int = 10,
                k: float = 2.0, max_days: int = 60) -> list[Trade]:
    """No new buys for 20 sessions after a bad event. Within 10 sessions after a good event (outside a blackout),
    buy the 9-bank basket at the close of the third up day in a row; sell when a day falls > 2x normal move (max 60)."""
    sessions = close.index
    b = basket(close, BANKS)
    nz = noise(b)
    up = (b.pct_change() > 0).astype(int)
    three_up = (up.rolling(3).sum() == 3)
    bad_idx = sorted(bad)
    trades, busy_until = [], -1
    for g in sorted(good):
        for j in range(g, min(g + window, len(sessions) - 1) + 1):
            if j <= busy_until:
                break
            blocked = any(0 <= j - bi <= blackout for bi in bad_idx)
            if blocked:
                continue
            if three_up.iloc[j]:
                x, still_open = noise_exit(b, nz, j, k, max_days)
                trades.append(Trade("regime", "BANKS", sessions[j].date().isoformat(), round(float(b.iloc[j]) * 100, 2),
                                    None if still_open else sessions[x].date().isoformat(),
                                    None if still_open else round(float(b.iloc[x]) * 100, 2),
                                    None if still_open else float(b.iloc[x] / b.iloc[j] - 1 - COST), good[g],
                                    open=still_open))
                busy_until = x
                break
    return trades


def status_regime(close: pd.DataFrame, bad: dict, good: dict, trades: list[Trade], blackout: int = 20) -> dict:
    sessions = close.index
    last = len(sessions) - 1
    recent_bad = [i for i in bad if last - i <= blackout]
    out: dict = {"blackout": blackout}
    if recent_bad:
        i = max(recent_bad)
        end = i + blackout
        out.update(state="blocked", bad_event=bad[i], bad_date=sessions[i].date().isoformat(),
                   sessions_left=end - last)
    else:
        out["state"] = "idle"
    if bad:
        i = max(bad)
        out["last_bad"] = {"date": sessions[i].date().isoformat(), "what": bad[i]}
    if good:
        i = max(good)
        out["last_good"] = {"date": sessions[i].date().isoformat(), "what": good[i]}
    open_trade = next((t for t in trades if t.open), None)
    if open_trade:
        b = basket(close, BANKS)
        e = session_index(sessions, pd.Timestamp(open_trade.entry_date))
        out.update(state="active", open_trade=asdict(open_trade),
                   ret_now=float(b.iloc[-1] / b.iloc[e] - 1 - COST), exit_drop=float(2.0 * noise(b).iloc[-1]))
    return out


# ───────────────────────── Rule 4 (lead): utilities after the government hits banks ─────────────────────────

BANK_HIT_TYPES = ("law_payment_holidays", "law_bank_tax", "chf_ruling", "knf_dividend_policy")


def rule_rotation(close: pd.DataFrame, events: pd.DataFrame, k: float = 2.0, max_days: int = 60) -> list[Trade]:
    """After a bank-negative policy event, buy the PGE/Tauron/Enea basket at the reaction-day close;
    sell when a day falls > 2x normal move (max 60 sessions)."""
    sessions = close.index
    u = basket(close, STATE_UTILS)
    nz = noise(u)
    trades, busy_until = [], -1
    ev = events[(events["category"] == "sector_shock") & events["event_type"].isin(BANK_HIT_TYPES)]
    for r in ev.sort_values("date").itertuples():
        if bank_event_sign(r.description) >= 0:
            continue
        i = reaction_day(sessions, r.date, r.time if isinstance(r.time, str) else None, r.session_timing)
        if i >= len(sessions) or i <= busy_until:
            continue
        x, still_open = noise_exit(u, nz, i, k, max_days)
        trades.append(Trade("rotation", "UTILS", sessions[i].date().isoformat(), round(float(u.iloc[i]) * 100, 2),
                            None if still_open else sessions[x].date().isoformat(),
                            None if still_open else round(float(u.iloc[x]) * 100, 2),
                            None if still_open else float(u.iloc[x] / u.iloc[i] - 1 - COST),
                            shorten(r.description), open=still_open))
        busy_until = x
    return trades


def status_rotation(close: pd.DataFrame, trades: list[Trade]) -> dict:
    open_trade = next((t for t in trades if t.open), None)
    out = {"state": "active" if open_trade else "idle"}
    if open_trade:
        u = basket(close, STATE_UTILS)
        e = session_index(close.index, pd.Timestamp(open_trade.entry_date))
        out.update(open_trade=asdict(open_trade), ret_now=float(u.iloc[-1] / u.iloc[e] - 1 - COST),
                   exit_drop=float(2.0 * noise(u).iloc[-1]))
    done = [t for t in trades if not t.open]
    if done:
        out["last_trade"] = asdict(done[-1])
    return out


# ───────────────────────── Summary ─────────────────────────

def summarize(trades: list[Trade]) -> dict:
    done = [t.ret_net for t in trades if not t.open and t.ret_net is not None]
    if not done:
        return {"n": 0}
    return {
        "n": len(done),
        "avg": sum(done) / len(done),
        "win_rate": sum(1 for x in done if x > 0) / len(done),
        "best": max(done),
        "worst": min(done),
    }


def run_all(prices: pd.DataFrame, bank_events: pd.DataFrame, sales: pd.DataFrame, today: dt.date | None = None) -> dict:
    close, opn = load_prices(prices)
    today_ts = pd.Timestamp(today or close.index[-1].date())
    # Only use complete sessions up to `today`.
    close, opn = close[close.index <= today_ts], opn[opn.index <= today_ts]

    releases = carparts_releases(sales)
    releases = releases[pd.to_datetime(releases["date"]) <= today_ts].reset_index(drop=True)
    # Published events only up to today; scheduled bank results stay (they define the next season).
    future = pd.to_datetime(bank_events["date"]) > today_ts
    bank_events = bank_events[~future | (bank_events["category"] == "bank_results")]
    cp = rule_carparts(close, opn, releases)
    seasons = bank_seasons(bank_events, close, today_ts)
    rt = rule_readthrough(close, seasons)
    bad, good = bank_bad_good_days(close, bank_events, seasons)
    rg = rule_regime(close, bad, good)
    rot = rule_rotation(close, bank_events)

    signals = {
        "carparts": {**status_carparts(close, releases, cp), "stats": summarize(cp)},
        "readthrough": {**status_readthrough(close, seasons, rt, bank_events, today_ts), "stats": summarize(rt)},
        "regime": {**status_regime(close, bad, good, rg), "stats": summarize(rg)},
        "rotation": {**status_rotation(close, rot), "stats": summarize(rot)},
    }
    return {
        "as_of": close.index[-1].date().isoformat(),
        "signals": signals,
        "trades": [asdict(t) for t in cp + rt + rg + rot],
        "seasons": [asdict(s) for s in seasons],
    }
