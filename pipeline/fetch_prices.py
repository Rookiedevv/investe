"""Download daily prices for every tracked instrument from Yahoo Finance.

Writes one long CSV: date,ticker,open,high,low,close,adj_close,volume.
Stooq (used for the original research) now blocks automated downloads,
so Yahoo is the live source. adj_close includes dividends.
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
    "WIG": "WIG.WA",
}

URL = "https://query1.finance.yahoo.com/v8/finance/chart/{s}?range=10y&interval=1d&events=div"


def fetch(symbol: str) -> list[dict]:
    req = urllib.request.Request(URL.format(s=symbol), headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
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
        if c is None or q["open"][i] is None:
            continue
        # Yahoo stamps Warsaw sessions at local open; the date part is the session day.
        day = dt.datetime.fromtimestamp(ts + res["meta"].get("gmtoffset", 0), dt.timezone.utc).date()
        rows.append({
            "date": day.isoformat(),
            "open": round(q["open"][i], 4), "high": round(q["high"][i], 4),
            "low": round(q["low"][i], 4), "close": round(c, 4),
            "adj_close": round(adj[i] if adj[i] is not None else c, 4),
            "volume": int(q["volume"][i] or 0),
        })
    # A session can appear twice when today's bar is still live; keep the last one.
    by_day = {r["date"]: r for r in rows}
    return [by_day[d] for d in sorted(by_day)]


def main(out_path: str) -> None:
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "ticker", "open", "high", "low", "close", "adj_close", "volume"])
        w.writeheader()
        for ticker, symbol in SYMBOLS.items():
            rows = fetch(symbol)
            for r in rows:
                w.writerow({"ticker": ticker, **r})
            print(f"{ticker}: {len(rows)} days, last {rows[-1]['date']} close {rows[-1]['close']}")
            time.sleep(0.5)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "prices.csv")
