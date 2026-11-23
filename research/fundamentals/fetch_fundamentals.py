"""Download quarterly financial statements for the research universe from biznesradar.pl.

For every ticker in research/prices_tickers.txt plus the pipeline's GPW stocks, fetches
  rzis  quarterly income statement        bilans quarterly balance sheet
  cf    quarterly cash flow               wr     market-value indicators (share count, price)
  dyw   dividend history
and stores the page's <table> blocks gzipped in research/fundamentals/raw/<TICKER>_<page>.html.gz.
parse_fundamentals.py turns them into tidy CSVs. Run by .github/workflows/fundamentals.yml.
Usage: fetch_fundamentals.py [TICKER ...]   (no args = whole universe)
"""
import datetime as dt
import gzip
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "research" / "fundamentals" / "raw"
PAGES = {
    "rzis": "raporty-finansowe-rachunek-zyskow-i-strat/{t},Q",
    "bilans": "raporty-finansowe-bilans/{t},Q",
    "cf": "raporty-finansowe-przeplywy-pieniezne/{t},Q",
    "wr": "wskazniki-wartosci-rynkowej/{t}",
    "dyw": "dywidenda/{t}",
}
NON_STOCK = {"WIG", "WIG20", "FW20"}
HDR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
       "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.5", "Accept": "text/html,application/xhtml+xml"}


def universe() -> list[str]:
    out = []
    for line in (ROOT / "research" / "prices_tickers.txt").read_text().splitlines():
        for t in line.split("#")[0].upper().split():
            if t not in out:
                out.append(t)
    sys.path.insert(0, str(ROOT / "pipeline"))
    import fetch_prices
    for t in fetch_prices.SYMBOLS:
        if t not in out and t not in NON_STOCK:
            out.append(t)
    return out


def get(url: str) -> tuple[str, str]:
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=60) as r:
                return r.read().decode("utf-8", "replace"), r.geturl()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(4 * (attempt + 1))
    raise RuntimeError(str(last))


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    tickers = [a.upper() for a in sys.argv[1:]] or universe()
    log = [f"fetched {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC, {len(tickers)} tickers"]
    for n, t in enumerate(tickers):
        for key, path in PAGES.items():
            url = "https://www.biznesradar.pl/" + path.format(t=t)
            try:
                html, final = get(url)
            except Exception as e:  # noqa: BLE001
                log.append(f"{t} {key}: ERROR {e}")
                continue
            tables = re.findall(r"<table\b.*?</table>", html, re.S)
            title = (re.search(r"<title>(.*?)</title>", html, re.S) or [None, ""])[1].strip()
            body = f"<!-- url {final} | title {title} -->\n" + "\n".join(tables)
            (RAW / f"{t}_{key}.html.gz").write_bytes(gzip.compress(body.encode("utf-8"), 9))
            if n == 0 and key in ("rzis", "wr"):  # one full page kept for parser debugging
                (RAW / f"_sample_{key}.html.gz").write_bytes(gzip.compress(html.encode("utf-8"), 9))
            log.append(f"{t} {key}: {len(html)} bytes, {len(tables)} tables, {final}")
            time.sleep(1.0)
    (RAW / "_fetch_log.txt").write_text("\n".join(log) + "\n")
    print("\n".join(log[-40:]))


if __name__ == "__main__":
    main()
