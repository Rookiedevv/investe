"""Download quarterly financial statements for the research universe from biznesradar.pl.

For every ticker in research/prices_tickers.txt plus the pipeline's GPW stocks, fetches the QUARTERLY
  rzis  income statement    bilans  balance sheet    cf  cash flow
and   wr  market-value indicators (share count, price per quarter).
biznesradar redirects /<page>/<TICKER>,Q to /<page>/<NAME> and drops the ",Q" (annual table), so the
page name is resolved first from the redirect and the quarterly page is requested as <NAME>,Q.
The report table of each page is stored, with the r/r, k/k and sector-comparison blocks removed, gzipped in
research/fundamentals/raw/<TICKER>_<page>.html.gz. parse_fundamentals.py turns them into tidy CSVs.
Usage: fetch_fundamentals.py [--top N] [--pages rzis,bilans] [--force] [TICKER ...]
  existing files are skipped unless --force; --top N = only the first N tickers of universe_order.txt (most liquid first).
The site stops answering after a few hundred pages in a short time, so requests go one at a time with a pause,
and the script stops as soon as two tickers in a row fail.
"""
import datetime as dt
import gzip
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "research" / "fundamentals" / "raw"
BASE = "https://www.biznesradar.pl/"
PAGES = {
    "rzis": "raporty-finansowe-rachunek-zyskow-i-strat/{n},Q",
    "bilans": "raporty-finansowe-bilans/{n},Q",
    "cf": "raporty-finansowe-przeplywy-pieniezne/{n},Q",
    "wr": "wskazniki-wartosci-rynkowej/{n}",
}
NON_STOCK = {"WIG", "WIG20", "FW20"}
DELAY = float(os.environ.get("FETCH_DELAY", 2.5))  # seconds between pages
BUDGET = int(os.environ.get("FETCH_BUDGET", 40 * 60))  # stop after this many seconds; the next pass continues with the missing files
HDR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
       "Accept-Language": "pl-PL,pl;q=0.9,en;q=0.5", "Accept": "text/html,application/xhtml+xml"}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def universe() -> list[str]:
    out = []
    order = ROOT / "research" / "fundamentals" / "universe_order.txt"   # most liquid first
    if order.exists():
        out = [t for t in order.read_text().split() if t]
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


def resolve(t: str) -> str:
    """biznesradar page name for a ticker (from the redirect of the report page; no redirect = ticker is the name)."""
    req = urllib.request.Request(BASE + PAGES["rzis"].format(n=t), headers=HDR)
    try:
        with urllib.request.build_opener(NoRedirect).open(req, timeout=30) as r:
            r.read(1)
            return t
    except urllib.error.HTTPError as e:
        loc = e.headers.get("Location") or ""
        if e.code in (301, 302, 303, 307, 308) and loc:
            return loc.rstrip("/").split("/")[-1].split(",")[0]
        raise


def get(url: str) -> tuple[str, str]:
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=45) as r:
                return r.read().decode("utf-8", "replace"), r.geturl()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(str(last))


def compact(html: str) -> str:
    m = re.search(r'<table[^>]*class="[^"]*report-table[^"]*".*?</table>', html, re.S)
    if not m:
        return ""
    t = re.sub(r"<div\b[^>]*>.*?</div>", "", m.group(0), flags=re.S)
    t = re.sub(r"</div>", "", t)
    return re.sub(r"\s+", " ", t)


def one(t: str, name: str, key: str) -> str:
    url = BASE + PAGES[key].format(n=name)
    try:
        html, final = get(url)
    except Exception as e:  # noqa: BLE001
        return f"{t} {key}: ERROR {e}"
    body = compact(html)
    if not body:
        return f"{t} {key}: NO TABLE ({len(html)} bytes, {final})"
    (RAW / f"{t}_{key}.html.gz").write_bytes(gzip.compress(f"<!-- url {final} -->\n{body}".encode("utf-8"), 9))
    return f"{t} {key}: {len(html)} -> {len(body)} bytes, {final}"


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    args = sys.argv[1:]
    force = "--force" in args
    top, pages = None, list(PAGES)
    for opt in ("--top", "--pages"):
        if opt in args:
            val = args[args.index(opt) + 1]
            args.remove(opt); args.remove(val)
            if opt == "--top":
                top = int(val)
            else:
                pages = [p for p in val.split(",") if p in PAGES]
    tickers = [a.upper() for a in args if not a.startswith("--")] or universe()[:top]
    log = [f"fetched {dt.datetime.now(dt.timezone.utc):%Y-%m-%d %H:%M} UTC, {len(tickers)} tickers, pages {','.join(pages)}, force {force}"]
    t0 = time.time()
    fails = 0
    for t in tickers:
        todo = [k for k in pages if force or not (RAW / f"{t}_{k}.html.gz").exists()]
        if not todo:
            continue
        try:
            name = resolve(t)
        except Exception as e:  # noqa: BLE001
            log.append(f"{t}: NOT FOUND ({e})")
            if "404" not in str(e):
                fails += 1
                if fails >= 2:
                    log.append("stopping: site not answering; rerun later for the rest")
                    break
            time.sleep(DELAY)
            continue
        res = []
        for k in todo:                      # one page at a time, slowly: be gentle with the site
            res.append(one(t, name, k))
            time.sleep(DELAY)
        log += res
        fails = fails + 1 if all("ERROR" in x for x in res) else 0
        if fails >= 2 or time.time() - t0 > BUDGET:
            log.append("stopping: site not answering or time budget used; rerun later for the rest")
            break
    log.append(f"done in {time.time() - t0:.0f}s")
    with open(RAW / "_fetch_log.txt", "a") as f:
        f.write("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
