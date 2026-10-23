"""Download daily prices for every tracked instrument from Yahoo Finance.

Writes one long CSV: date,ticker,open,high,low,close,adj_close,volume.
Stooq (used for the original research) now blocks automated downloads,
so Yahoo is the live source. adj_close includes dividends.

Two groups:
- SYMBOLS: GPW stocks and WIG (10 years, enough for the sector rules).
- MARKET: WIG20 and the foreign series used by the WIG20 dip model
  (full history; all are known before the Warsaw open the next day).
"""
import csv
import datetime as dt
import json
import sys
import time
import urllib.request

SYMBOLS = {
    "PKO": "PKO.WA", "PEO": "PEO.WA", "EBP": "EBP.WA", "MBK": "MBK.WA", "ING": "ING.WA",
    "MIL": "MIL.WA", "ALR": "ALR.WA", "BHW": "BHW.WA", "BNP": "BNP.WA",
    "PGE": "PGE.WA", "TPE": "TPE.WA", "ENA": "ENA.WA", "PEP": "PEP.WA",
    "CAR": "CAR.WA", "APR": "APR.WA",
    "WIG": ["WIG.WA"],  # Yahoo: current day only; accumulated like WIG20
}

# Series whose history Yahoo no longer serves: keep every row ever fetched (plus Stooq seeds).
ACCUMULATE = {"WIG20", "WIG"}

# ticker -> (yahoo symbols to try in order, name, sector for the instruments table, market)
MARKET = {
    # Yahoo serves only the current day for GPW indices; these rows are ACCUMULATED in
    # data/prices/<T>.csv by run.py (older history comes from Stooq files Zuzanna provides once).
    "WIG20": (["WIG20.WA"], "WIG20 (indeks)", "index", "GPW"),
    # Index-tracking ETFs with real daily history, used as WIG20 proxies for the years before
    # the accumulated index rows exist.
    "ETFW20L": (["ETFW20L.WA"], "Lyxor/Amundi WIG20 UCITS ETF", "index", "GPW"),
    "ETFBW20TR": (["ETFBW20TR.WA"], "Beta ETF WIG20TR", "index", "GPW"),
    "SPX": (["^GSPC"], "S&P 500", "index", "US"),
    "NDQ": (["^IXIC"], "Nasdaq Composite", "index", "US"),
    "DAX": (["^GDAXI"], "DAX", "index", "DE"),
    "VIX": (["^VIX"], "VIX", "index", "US"),
    "BRENT": (["BZ=F"], "Brent (futures)", "other", "ICE"),
    "EURPLN": (["EURPLN=X"], "EUR/PLN", "other", "FX"),
    "USDPLN": (["USDPLN=X"], "USD/PLN", "other", "FX"),
}

# Explicit period1/period2: with range=max Yahoo silently returns quarterly bars.
URL = ("https://query1.finance.yahoo.com/v8/finance/chart/{s}"
       "?period1={p1}&period2={p2}&interval=1d&events=div")
YEAR = 365 * 86400


def fetch(symbol: str, years: int = 10) -> list[dict]:
    now = int(time.time())
    req = urllib.request.Request(URL.format(s=symbol, p1=max(0, now - years * YEAR), p2=now + 86400),
                                 headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                res = json.load(r)["chart"]["result"][0]
            break
        except Exception as e:  # network hiccup or rate limit: back off and retry
            if attempt == 3:
                raise RuntimeError(f"{symbol}: {e}") from e
            time.sleep(3 * (attempt + 1))
    q = res["indicators"]["quote"][0]
    adj = (res["indicators"].get("adjclose") or [{}])[0].get("adjclose") or q["close"]
    rows = []
    for i, ts in enumerate(res["timestamp"]):
        c = q["close"][i]
        if c is None or c <= 0:
            continue
        # Index bars sometimes lack open/high/low; fall back to the close.
        o, h, lo = (q["open"][i] or c), (q["high"][i] or c), (q["low"][i] or c)
        if o <= 0 or h <= 0 or lo <= 0:
            o, h, lo = c, c, c
        # Yahoo stamps sessions at the local open; the date part is the session day.
        day = dt.datetime.fromtimestamp(ts + res["meta"].get("gmtoffset", 0), dt.timezone.utc).date()
        rows.append({
            "date": day.isoformat(),
            "open": round(o, 4), "high": round(max(h, o, c), 4),
            "low": round(min(lo, o, c), 4), "close": round(c, 4),
            "adj_close": round(adj[i] if adj[i] is not None else c, 4),
            "volume": int(q["volume"][i] or 0),
        })
    # A session can appear twice when today's bar is still live; keep the last one.
    by_day = {r["date"]: r for r in rows}
    return [by_day[d] for d in sorted(by_day)]


def fetch_any(symbols: list[str], years: int) -> tuple[list[dict], str]:
    """First symbol that returns a real daily series (> 200 rows); else the longest one."""
    best: tuple[list[dict], str] = ([], symbols[0])
    for sym in symbols:
        try:
            rows = fetch(sym, years)
        except Exception as e:
            print(f"  {sym}: {e}")
            continue
        if len(rows) > 200 or len(symbols) == 1:
            return rows, sym
        if len(rows) > len(best[0]):
            best = (rows, sym)
    return best


def main(out_path: str, log_path: str | None = None) -> None:
    """Stocks (SYMBOLS) must all succeed; a market series that fails is logged and skipped."""
    jobs = ([(t, [s] if isinstance(s, str) else s, 10, t != "WIG") for t, s in SYMBOLS.items()]
            + [(t, m[0], 60, False) for t, m in MARKET.items()])
    log = [f"fetched {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC"]
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "ticker", "open", "high", "low", "close", "adj_close", "volume"])
        w.writeheader()
        for ticker, symbols, years, required in jobs:
            rows, used = fetch_any(symbols, years)
            if not rows:
                if required:
                    raise RuntimeError(f"{ticker}: no data from Yahoo ({symbols})")
                line = f"{ticker}: NO DATA (tried {symbols})"
            else:
                for r in rows:
                    w.writerow({"ticker": ticker, **r})
                line = f"{ticker} ({used}): {len(rows)} days, {rows[0]['date']} .. {rows[-1]['date']}, last close {rows[-1]['close']}"
            print(line)
            log.append(line)
            time.sleep(0.5)
    if log_path:
        with open(log_path, "w") as f:
            f.write("\n".join(log) + "\n")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "prices.csv")
