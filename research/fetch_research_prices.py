"""Fetch daily Yahoo history for research-only tickers (not loaded into Supabase).

Reads research/prices_tickers.txt (GPW tickers, one or more per line, '#' comments),
writes research/prices/<TICKER>.csv (date,open,high,low,close,adj_close,volume)
and research/prices/_fetch_log.txt. A ticker Yahoo doesn't serve is logged and skipped.
Run by .github/workflows/research-prices.yml (manual or on change of the ticker list).
"""
import csv
import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))
import fetch_prices  # noqa: E402

OUT = ROOT / "research" / "prices"
COLS = ["date", "open", "high", "low", "close", "adj_close", "volume"]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tickers = []
    for line in (ROOT / "research" / "prices_tickers.txt").read_text().splitlines():
        for t in line.split("#")[0].upper().split():  # one or several tickers per line
            if t not in tickers:
                tickers.append(t)
    log = [f"fetched {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC"]
    for t in tickers:
        rows, used = fetch_prices.fetch_any([f"{t}.WA"], 12)
        if not rows:
            log.append(f"{t}: NO DATA")
            continue
        with open(OUT / f"{t}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            w.writeheader()
            for r in rows:
                w.writerow({k: r[k] for k in COLS})
        log.append(f"{t} ({used}): {len(rows)} days, {rows[0]['date']} .. {rows[-1]['date']}")
    fout = ROOT / "research" / "prices_foreign"
    fout.mkdir(parents=True, exist_ok=True)
    ff = ROOT / "research" / "foreign_tickers.txt"
    for line in (ff.read_text().splitlines() if ff.exists() else []):
        sym = line.split("#")[0].strip()
        if not sym:
            continue
        rows, used = fetch_prices.fetch_any([sym], 12)
        if not rows:
            log.append(f"{sym}: NO DATA")
            continue
        with open(fout / f"{sym}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            w.writeheader()
            for r in rows:
                w.writerow({k: r[k] for k in COLS})
        log.append(f"{sym}: {len(rows)} days, {rows[0]['date']} .. {rows[-1]['date']}")
    (OUT / "_fetch_log.txt").write_text("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
