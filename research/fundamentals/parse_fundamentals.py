"""Parse the biznesradar tables saved by fetch_fundamentals.py into tidy CSVs.

Output (research/fundamentals/):
  income_q.csv, balance_q.csv, cashflow_q.csv  one row per ticker x quarter, all statement lines as columns
                                               (thousands of PLN), plus pub_date = publication date of the report
  market_q.csv                                  share count, price and per-share ratios at each quarter (biznesradar)
  income_y.csv, balance_y.csv, cashflow_y.csv   the same for annual statements, where fetched
  names.csv                                     ticker -> biznesradar page name
Quarterly income / cash-flow values are single-quarter figures (not year-to-date).
"""
import csv
import gzip
import html as htmlmod
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FD = ROOT / "research" / "fundamentals"
RAW = FD / "raw"
TAG = re.compile(r"<[^>]+>")


def num(s: str):
    s = s.replace("\xa0", "").replace(" ", "").replace(",", ".")
    if s in ("", "-"):
        return ""
    try:
        return float(s)
    except ValueError:
        return s  # dates and other text


def parse_table(text: str):
    """-> (periods, {field: [values]}) from the first report-table in the saved html."""
    m = re.search(r'<table[^>]*class="[^"]*report-table[^"]*".*?</table>', text, re.S)
    if not m:
        return [], {}
    t = m.group(0)
    rows = re.findall(r"<tr\b([^>]*)>(.*?)</tr>", t, re.S)
    periods = []
    for th in re.findall(r"<th\b[^>]*class=\"thq[^\"]*\"[^>]*>(.*?)</th>", rows[0][1], re.S):
        lab = re.sub(r"<span>.*?</span>", "", th, flags=re.S)
        periods.append(TAG.sub("", lab).strip())
    out = {}
    for attrs, body in rows[1:]:
        f = re.search(r'data-field="([^"]+)"', attrs)
        if not f:
            continue
        cells = re.split(r'<td\b[^>]*class="h[^"]*"[^>]*>', body)[1:]
        vals = []
        for c in cells:
            c = c.split("<div", 1)[0]
            vals.append(num(htmlmod.unescape(TAG.sub("", c)).strip()))
        out[f.group(1)] = vals[:len(periods)]
    return periods, out


def main() -> None:
    files = sorted(RAW.glob("*.html.gz"))
    books = {}   # (stmt, freq) -> list of dict rows
    names = {}
    for f in files:
        if f.name.startswith("_"):
            continue
        stem = f.name[:-8]
        parts = stem.split("_")
        tick, key = parts[0], parts[1]
        text = gzip.decompress(f.read_bytes()).decode("utf-8", "replace")
        url = (re.search(r"<!-- url (\S+)", text) or [None, ""])[1]
        nm = url.rstrip("/").split("/")[-1].split(",")[0]
        if nm:
            names[tick] = nm
        periods, data = parse_table(text)
        if not periods:
            continue
        freq = "q" if all("/Q" in p for p in periods[:3]) else "y"
        if key == "wr":
            freq = "q"
        for k, p in enumerate(periods):
            if not re.match(r"^\d{4}", p):
                continue  # trailing-12-month helper column
            row = {"ticker": tick, "period": p}
            for fld, vals in data.items():
                if k < len(vals):
                    row["pub_date" if fld == "PrimaryReport" else fld] = vals[k]
            if any(v != "" for kk, v in row.items() if kk not in ("ticker", "period", "pub_date")):
                books.setdefault((key, freq), []).append(row)
    label = {"rzis": "income", "bilans": "balance", "cf": "cashflow", "wr": "market"}
    for (key, freq), rows in books.items():
        cols = ["ticker", "period", "pub_date"]
        for r in rows:
            for c in r:
                if c not in cols:
                    cols.append(c)
        if key == "wr":
            cols.remove("pub_date")
        with open(FD / f"{label[key]}_{freq}.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(label[key], freq, len(rows), "rows,", len({r['ticker'] for r in rows}), "tickers,", len(cols), "cols")
    with open(FD / "names.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ticker", "biznesradar_name"])
        for t in sorted(names):
            w.writerow([t, names[t]])


if __name__ == "__main__":
    main()
