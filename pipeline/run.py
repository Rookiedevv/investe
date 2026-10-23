"""Nightly job: fetch prices, load research events, compute signals, write everything to Supabase.

Needs env SUPABASE_URL and SUPABASE_SECRET_KEY (GitHub repository secret).
Run locally without a key to only compute and print: python pipeline/run.py --dry
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import fetch_prices  # noqa: E402
import signals as S  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

TIMING = {"after_close": "after", "pre_open": "before", "intraday": "during", "before": "before",
          "during": "during", "after": "after", "non_trading_day": "non_trading_day"}


# ───────────────────────── Supabase REST ─────────────────────────

class Supa:
    def __init__(self, url: str, key: str):
        self.base = url.rstrip("/") + "/rest/v1"
        self.key = key

    def _req(self, method: str, path: str, body=None, prefer: str | None = None):
        headers = {"apikey": self.key, "Content-Type": "application/json"}
        if not self.key.startswith("sb_"):
            headers["Authorization"] = f"Bearer {self.key}"  # legacy service_role JWT
        if prefer:
            headers["Prefer"] = prefer
        data = None if body is None else json.dumps(body, default=_json_default).encode()
        req = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{method} {path}: {e.code} {e.read().decode()[:400]}") from None

    def upsert(self, table: str, rows: list[dict], on_conflict: str, chunk: int = 1000):
        for i in range(0, len(rows), chunk):
            self._req("POST", f"/{table}?on_conflict={on_conflict}", rows[i:i + chunk],
                      "resolution=merge-duplicates,return=minimal")

    def insert(self, table: str, rows: list[dict], chunk: int = 500):
        for i in range(0, len(rows), chunk):
            self._req("POST", f"/{table}", rows[i:i + chunk], "return=minimal")

    def delete(self, table: str, filt: str):
        self._req("DELETE", f"/{table}?{filt}", prefer="return=minimal")


def _json_default(o):
    if hasattr(o, "item"):
        return o.item()
    if isinstance(o, (dt.date, pd.Timestamp)):
        return o.isoformat()
    raise TypeError(type(o))


def clean(v):
    """JSON-safe value: NaN -> None, numpy -> python."""
    if isinstance(v, dict):
        return {k: clean(x) for k, x in v.items()}
    if isinstance(v, list):
        return [clean(x) for x in v]
    if hasattr(v, "item"):
        v = v.item()
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v


def blank(v):
    return None if v is None or (isinstance(v, float) and math.isnan(v)) or v == "" else v


# ───────────────────────── Events from the research CSVs ─────────────────────────

def load_events() -> list[dict]:
    rows: list[dict] = []
    bank = pd.read_csv(DATA / "bank_events.csv", dtype=str).fillna("")
    for r in bank.itertuples():
        sign = S.bank_event_sign(r.description) if r.category == "sector_shock" else 0
        rows.append(dict(date=r.date, time=blank(r.time), session_timing=TIMING.get(r.session_timing, "unknown"),
                         ticker=r.ticker, sector="banks", category=r.category, event_type=r.event_type,
                         period=blank(r.period), status=r.status or "published", sign=sign,
                         description=r.description, source_url=blank(r.source_url)))
    util = pd.read_csv(DATA / "util_events.csv", dtype=str).fillna("")
    for r in util.itertuples():
        rows.append(dict(date=r.date, time=blank(r.time), session_timing=TIMING.get(r.session_timing, "unknown"),
                         ticker=r.ticker, sector="utilities", category="utility_news", event_type=r.event_type,
                         period=None, status="published", sign=int(r.sign or 0),
                         description=r.description, source_url=blank(r.source_url)))
    pol = pd.read_csv(DATA / "political_events.csv", dtype=str).fillna("")
    for r in pol.itertuples():
        rows.append(dict(date=r.date, time=blank(r.time), session_timing=TIMING.get(r.session_timing, "unknown"),
                         ticker=r.scope, sector="politics", category="politics", event_type=r.category,
                         period=None, status="published", sign=0,
                         description=r.description, source_url=blank(r.source_url)))
    cp = pd.read_csv(DATA / "carparts_sales.csv", dtype=str).fillna("")
    for r in cp.itertuples():
        kind = "monthly_sales" if r.period else "financial_report"
        desc = (f"Monthly sales {r.period}: {r.sales_pln_m} m PLN" + (f", {r.yoy_pct}% y/y" if r.yoy_pct else "")
                if r.period else r.description.rsplit("; ", 1)[-1])
        rows.append(dict(date=r.date, time=blank(r.time), session_timing=TIMING.get(r.session_timing, "unknown"),
                         ticker=r.ticker, sector="carparts", category="company_results", event_type=kind,
                         period=blank(r.period), status="published", sign=0,
                         description=desc, source_url=blank(r.source_url)))
    for r in rows:
        r["source"] = "research"
    return rows


def sales_rows(releases: pd.DataFrame) -> list[dict]:
    return [clean(dict(ticker=r.ticker, period=r.period, release_date=r.date, release_time=blank(r.time),
                       sales_pln_m=r.sales_pln_m, yoy_pct=r.yoy_pct, accel=r.accel))
            for r in releases.itertuples()]


# ───────────────────────── Snapshots ─────────────────────────

def write_snapshots(prices: pd.DataFrame, folder: Path) -> None:
    """One CSV per ticker: date,open,high,low,close,adj_close,volume (sorted by date)."""
    folder.mkdir(parents=True, exist_ok=True)
    cols = ["date", "open", "high", "low", "close", "adj_close", "volume"]
    for ticker, g in prices.groupby("ticker"):
        g.sort_values("date")[cols].to_csv(folder / f"{ticker}.csv", index=False)


# ───────────────────────── Main ─────────────────────────

def main(dry: bool = False) -> None:
    started = dt.datetime.now(dt.timezone.utc)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "prices.csv"
        (DATA / "prices").mkdir(parents=True, exist_ok=True)
        fetch_prices.main(str(path), str(DATA / "prices" / "_fetch_log.txt"))
        prices = pd.read_csv(path)

    # Drop today's bar if the job runs before the session is over (Warsaw close 17:05).
    now_waw = dt.datetime.now(ZoneInfo("Europe/Warsaw"))
    today = now_waw.date().isoformat()
    if now_waw.hour < 17 or (now_waw.hour == 17 and now_waw.minute < 15):
        prices = prices[prices["date"] < today]

    # Snapshots per ticker, committed to the repo by the workflow (data/prices/<TICKER>.csv),
    # so research sessions can read the history from GitHub without any upload.
    write_snapshots(prices, DATA / "prices")

    bank = pd.read_csv(DATA / "bank_events.csv", dtype=str).fillna("")
    sales = pd.read_csv(DATA / "carparts_sales.csv", dtype=str)
    stocks = prices[~prices["ticker"].isin(set(fetch_prices.MARKET) | {"WIG"})]
    result = S.run_all(stocks, bank, sales)
    releases = S.carparts_releases(sales)

    stale = [t for t, d in stocks.groupby("ticker")["date"].max().items()
             if (pd.Timestamp(result["as_of"]) - pd.Timestamp(d)).days > 5]
    print(json.dumps({k: {"state": v["state"], "stats": v["stats"]} for k, v in result["signals"].items()},
                     indent=1, default=str))
    if dry:
        return

    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SECRET_KEY")
    if not url or not key:
        print("::error title=daily-update::SUPABASE_SECRET_KEY is not set (GitHub → Settings → Secrets → Actions)")
        sys.exit(1)
    db = Supa(url, key)

    # Market series (WIG20, S&P 500, ...) must exist in instruments before their prices (FK).
    db.upsert("instruments", [dict(ticker=t, name=m[1], sector=m[2], market=m[3], watched=False)
                              for t, m in fetch_prices.MARKET.items()], "ticker")

    # Market series are replaced whole (an earlier run stored quarterly bars for them under daily dates).
    present = sorted(set(prices["ticker"]) & set(fetch_prices.MARKET))
    if present:
        db.delete("prices", "ticker=in.(" + ",".join(present) + ")")

    price_rows = [clean(dict(ticker=r.ticker, date=r.date, open=r.open, high=r.high, low=r.low, close=r.close,
                             adj_close=r.adj_close, volume=r.volume)) for r in prices.itertuples()]
    db.upsert("prices", price_rows, "ticker,date")

    db.delete("events", "source=eq.research")
    db.insert("events", [clean(r) for r in load_events()])

    db.delete("sales_releases", "ticker=neq.__none__")
    db.insert("sales_releases", sales_rows(releases))

    db.upsert("signals", [clean(dict(id=k, state=v["state"], data=v, as_of=result["as_of"],
                                     updated_at=started.isoformat()))
                          for k, v in result["signals"].items()], "id")

    db.delete("backtest_trades", "rule=neq.__none__")
    db.insert("backtest_trades", [clean({k: t[k] for k in ("rule", "ticker", "entry_date", "entry_price", "exit_date",
                                                           "exit_price", "ret_net", "reason", "open")})
                                  for t in result["trades"]])

    msg = "ok" if not stale else f"stale prices: {', '.join(stale)}"
    db.insert("pipeline_runs", [dict(ran_at=started.isoformat(), as_of=result["as_of"],
                                     status="ok" if not stale else "warning", message=msg)])
    print(f"Loaded {len(price_rows)} prices, signals as of {result['as_of']} ({msg})")
    print(f"::notice title=daily-update::{len(price_rows)} prices, signals as of {result['as_of']}: "
          + ", ".join(f"{k}={v['state']}" for k, v in result["signals"].items()) + f" ({msg})")


if __name__ == "__main__":
    try:
        main(dry="--dry" in sys.argv)
    except SystemExit:
        raise
    except Exception as e:  # surface the reason as a GitHub annotation, readable without the full log
        print(f"::error title=daily-update failed::{type(e).__name__}: {str(e)[:900]}")
        raise
