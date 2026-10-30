"""Build car-registration CSV from harvested money.pl (ISBnews) headlines.
New-format money.pl article IDs (e.g. ...-6346221911967361a.html) encode the
publication time: id / 4096 = Unix epoch milliseconds (UTC)."""
import csv, re, datetime as dt, sys
from zoneinfo import ZoneInfo
RAW = sys.argv[1]; OUT = sys.argv[2]
WAW = ZoneInfo("Europe/Warsaw")
ROM = {r:i+1 for i,r in enumerate("I II III IV V VI VII VIII IX X XI XII".split())}
# Old sequential-ID articles (2017-2018): month inferred from ID order + Roman month in title.
OLD_MONTH = {2294692:"2017-03",2342274:"2017-06",2342474:"2017-06",2351900:"2017-07",
 2361892:"2017-08",2362142:"2017-08",2372739:"2017-09",2385206:"2017-10",2385636:"2017-10",
 2393112:"2017-11",2395438:"2017-12",2397898:"2018-01",2398051:"2018-01",2400118:"2018-02",
 2405330:"2018-04",2408034:"2018-05",2410546:"2018-06",2414990:"2018-08"}
rows = {}
for line in open(RAW, encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    rom, yoy, url = p[0], p[1], p[2]
    src = p[3] if len(p) > 3 else "Samar"
    if rom in ("?", "FY") or yoy == "?":
        continue
    m = re.search(r"-(\d{15,17})a\.html$", url)
    if m:
        ts = dt.datetime.fromtimestamp(int(m.group(1))/4096/1000, dt.UTC).astimezone(WAW)
        ref_y = ts.year if ROM[rom] < ts.month else ts.year - 1
        month = f"{ref_y}-{ROM[rom]:02d}"
        rd, rt = ts.date().isoformat(), ts.strftime("%H:%M") + " Europe/Warsaw (money.pl/ISBnews publication time)"
    else:
        oid = int(re.search(r",(\d+)\.html$", url).group(1))
        if oid not in OLD_MONTH:
            continue  # pre-2017 or unidentifiable
        month = OLD_MONTH[oid]
        rd, rt = "", "unknown; old money.pl ID not decodable; Samar/PZPM normally publish on working days 1-5 of the following month"
    if not month.startswith(("2017","2018","2019","2020","2021","2022","2023","2024","2025","2026")):
        continue
    key = month
    # prefer Samar headline over PZPM duplicate for the same month
    if key in rows and src == "PZPM":
        continue
    rows[key] = dict(series="new_regs_cars_and_lcv_le3.5t_samar" if src=="Samar" else "new_regs_cars_and_lcv_le3.5t_pzpm",
                     month=month, release_date=rd, release_time_if_known=rt, value="", yoy_pct=yoy.lstrip("+"), source_url=url)
# Single 2026 passenger-car point found via headline + dated URL
rows["2026-09"] = dict(series="new_regs_passenger_cars_samar", month="2026-09", release_date="2026-10-05",
    release_time_if_known="upper bound: date of imagazine.pl article; Samar release may be earlier (1-2 Oct)",
    value="", yoy_pct="12.5", source_url="https://ecoekonomia.pl/samar-rejestracje-nowych-aut-wzrosly-o-125-r-r-we-ix-udzial-chinskich-marek-156/ ; https://imagazine.pl/2026/10/05/rejestracje-nowych-aut-wrzesien-2026-samar-rekord-mg-spadek-bev/")
cols = "series,month,release_date,release_time_if_known,value,yoy_pct,source_url".split(",")
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, cols); w.writeheader()
    for k in sorted(rows): w.writerow(rows[k])
print(len(rows), "rows")
