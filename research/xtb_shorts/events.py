"""Event lists for the XTB-short tests of existing avoid signals (29 Oct 2026).

Transcribed from the project's research files (claude/construction_contracts.csv,
claude/retail_company_reports.csv, claude/peer_results.csv, claude/gaming_events.csv,
claude/index_changes.csv). Timing: 'before' / 'during' -> the news is tradable at that
day's close; 'after' / 'unknown' / weekend -> the first tradable close is the next session.
"""

# Polimex (PXM) contracts: (date, timing, company value mln zł)
PXM_CONTRACTS = [
    ("2018-03-01", "after", 65.0), ("2018-03-12", "during", 65.0), ("2018-09-25", "during", 199.3),
    ("2018-12-17", "during", 326.89), ("2019-01-16", "during", 326.89), ("2019-09-25", "during", 1159.9),
    ("2019-10-22", "during", 55.82), ("2019-11-19", "after", 72.44), ("2019-11-21", "during", 107.0),
    ("2019-12-03", "after", 72.44), ("2020-01-30", "during", 1515.1), ("2020-03-27", "after", 106.8),
    ("2020-07-31", "during", 99.8), ("2020-08-20", "after", 91.6), ("2020-09-04", "during", 99.8),
    ("2020-10-07", "during", 161.0), ("2020-11-05", "after", 91.57), ("2021-04-29", "after", 79.7),
    ("2021-06-02", "during", 201.58), ("2021-06-23", "during", 1425.8), ("2021-08-05", "during", 77.05),
    ("2021-10-28", "after", 59.5), ("2021-11-30", "during", 65.0), ("2022-01-04", "during", 241.2),
    ("2022-04-12", "after", 140.0), ("2022-05-05", "during", 61.96), ("2022-06-21", "during", 69.57),
    ("2022-09-26", "after", 359.3), ("2022-11-03", "during", 115.0), ("2022-11-25", "after", 143.27),
    ("2023-02-09", "during", 1374.94), ("2023-07-05", "during", 3430.54), ("2023-09-08", "after", 216.06),
    ("2023-09-11", "after", 90.0), ("2023-09-21", "during", 386.2), ("2023-12-21", "during", 204.9),
    ("2024-01-18", "after", 800.0), ("2024-04-03", "during", 105.15), ("2024-07-10", "during", 117.3),
    ("2025-01-16", "during", 81.9), ("2025-01-20", "after", 63.9), ("2025-04-17", "during", 126.2),
    ("2025-05-27", "during", 320.0), ("2025-05-30", "after", 55.0), ("2025-06-10", "after", 202.7),
    ("2025-09-15", "during", 1665.0), ("2025-10-04", "after", 73.71), ("2025-11-27", "after", 384.9),
    ("2026-03-04", "during", 2304.0), ("2026-09-24", "during", 292.17),
]
# EUR-only contracts converted at ~4.3 zł/EUR (2021-11-30 EUR 14.3m, 2022-04-12 EUR 30.4m,
# 2022-11-03 EUR 24.3m, 2023-09-11 EUR 19.9m, 2024-01-18 EUR 184.8m). Two same-day 2026-03-04
# OCGT contracts merged.

# Approximate PXM revenue (mln zł) of the previous year, for the "size >= 10% of revenue" version.
# 2022-2025 from quarterly sums in claude/construction_quarterly_results.csv; earlier years rounded.
PXM_PREV_REV = {2018: 2600, 2019: 2150, 2020: 2480, 2021: 3060, 2022: 2800, 2023: 3780,
                2024: 3010, 2025: 2860, 2026: 3800}

# Eurocash (EUR) and Dino (DNP) results / prelims: (date, timing)
EUR_REPORTS = [
    ("2018-02-28", "before"), ("2018-05-11", "before"), ("2018-08-29", "before"), ("2018-11-09", "before"),
    ("2019-02-28", "before"), ("2019-05-10", "before"), ("2019-08-28", "before"), ("2019-11-13", "before"),
    ("2020-03-13", "before"), ("2020-05-13", "before"), ("2020-08-25", "before"), ("2020-11-13", "before"),
    ("2021-03-11", "before"), ("2021-05-13", "before"), ("2021-07-20", "after"), ("2021-08-25", "before"),
    ("2021-11-10", "before"), ("2022-03-09", "after"), ("2022-05-12", "before"), ("2022-08-29", "after"),
    ("2022-11-10", "before"), ("2023-03-28", "before"), ("2023-05-12", "before"), ("2023-08-29", "before"),
    ("2023-11-10", "before"), ("2024-04-19", "before"), ("2024-05-13", "after"), ("2024-08-28", "before"),
    ("2024-11-14", "before"), ("2025-02-07", "after"), ("2025-05-15", "before"), ("2025-08-28", "before"),
    ("2025-11-24", "before"), ("2026-04-29", "after"), ("2026-05-11", "before"), ("2026-08-27", "before"),
]
DNP_REPORTS = [
    ("2018-03-19", "before"), ("2018-05-15", "after"), ("2018-08-21", "after"), ("2018-11-08", "after"),
    ("2019-03-14", "after"), ("2019-05-09", "after"), ("2019-08-19", "after"), ("2019-11-07", "after"),
    ("2020-03-13", "before"), ("2020-05-15", "after"), ("2020-08-21", "before"), ("2020-11-06", "before"),
    ("2021-03-12", "before"), ("2021-05-07", "before"), ("2021-08-20", "before"), ("2021-11-05", "before"),
    ("2022-03-10", "after"), ("2022-05-05", "after"), ("2022-08-18", "after"), ("2022-11-03", "after"),
    ("2023-03-23", "after"), ("2023-05-04", "after"), ("2023-08-17", "after"), ("2023-11-02", "after"),
    ("2024-03-21", "after"), ("2024-05-09", "after"), ("2024-08-22", "after"), ("2024-11-07", "after"),
    ("2025-02-27", "after"), ("2025-04-14", "before"), ("2025-05-15", "after"), ("2025-08-21", "after"),
    ("2025-11-06", "after"), ("2026-03-26", "after"), ("2026-05-14", "after"), ("2026-08-20", "after"),
]

# Inditex / H&M result days (all published 08:00 CET, before Warsaw opens): (date, own reaction %)
PEER_DAYS = [
    ("2021-06-09", -2.17), ("2021-06-15", -2.86), ("2021-07-01", -1.08), ("2021-09-15", -3.06),
    ("2021-09-30", -3.43), ("2021-12-15", -5.22), ("2022-01-28", 5.05), ("2022-03-15", -3.15),
    ("2022-03-16", -2.46), ("2022-03-31", -12.91), ("2022-06-08", 6.35), ("2022-06-15", -6.50),
    ("2022-06-29", 2.20), ("2022-09-14", 3.78), ("2022-09-15", -4.73), ("2022-09-29", -5.85),
    ("2022-12-14", 3.07), ("2022-12-15", -6.85), ("2023-01-27", -4.12), ("2023-03-15", -8.47),
    ("2023-03-30", 16.31), ("2023-06-07", 5.69), ("2023-06-15", 3.67), ("2023-06-29", 18.18),
    ("2023-09-13", -0.47), ("2023-09-15", -7.39), ("2023-09-28", -4.88), ("2023-12-13", -0.23),
    ("2023-12-15", 0.48), ("2024-01-31", -12.37), ("2024-03-13", 7.74), ("2024-03-27", 15.19),
    ("2024-06-05", 3.73), ("2024-06-27", -12.97), ("2024-09-11", 4.54), ("2024-09-26", -4.60),
    ("2024-12-11", -6.54), ("2025-01-30", -3.44), ("2025-03-12", -7.50), ("2025-03-27", 0.41),
    ("2025-06-11", -4.37), ("2025-06-26", 3.74), ("2025-09-10", 6.52), ("2025-09-25", 9.78),
    ("2025-12-03", 8.86), ("2026-01-29", -0.73), ("2026-03-11", 0.53), ("2026-03-26", -2.18),
    ("2026-06-03", 1.48), ("2026-06-25", -0.59), ("2026-09-09", -3.61), ("2026-09-24", -2.02),
]

# Gaming launches (flagship / own or published titles): (date, ticker, timing, label)
LAUNCHES = [
    ("2016-05-31", "CDR", "unknown", "Witcher 3 Blood and Wine"),
    ("2018-04-24", "11B", "unknown", "Frostpunk"),
    ("2018-05-29", "11B", "unknown", "Moonlighter"),
    ("2018-10-23", "CDR", "unknown", "Gwent/Thronebreaker"),
    ("2019-09-03", "11B", "unknown", "Children of Morta"),
    ("2019-10-15", "CDR", "unknown", "Witcher 3 Switch"),
    ("2020-12-10", "CDR", "before", "Cyberpunk 2077"),
    ("2017-04-25", "CIG", "unknown", "Sniper Ghost Warrior 3"),
    ("2019-11-22", "CIG", "unknown", "SGW Contracts"),
    ("2021-06-04", "CIG", "unknown", "SGW Contracts 2"),
    ("2023-10-13", "CIG", "unknown", "Lords of the Fallen"),
    ("2017-07-28", "PLW", "during", "Car Mechanic Simulator 2018"),
    ("2018-05-17", "PLW", "during", "House Flipper"),
    ("2021-08-11", "PLW", "unknown", "Car Mechanic Simulator 2021"),
    ("2023-12-14", "PLW", "unknown", "House Flipper 2"),
    ("2021-02-19", "HUG", "during", "IPO day (excluded)"),
    ("2023-09-26", "CDR", "unknown", "Phantom Liberty"),
    ("2024-03-04", "11B", "unknown", "The Thaumaturge"),
    ("2024-05-02", "11B", "unknown", "Indika"),
    ("2024-09-20", "11B", "after", "Frostpunk 2"),
    ("2025-06-05", "CDR", "unknown", "Cyberpunk Switch 2"),
    ("2025-06-13", "11B", "unknown", "The Alters"),
    ("2025-09-18", "11B", "unknown", "Frostpunk 2 consoles"),
    ("2025-11-19", "11B", "unknown", "Moonlighter 2 EA"),
    ("2026-09-02", "11B", "unknown", "Moonlighter 2 1.0"),
    ("2026-09-29", "CDR", "unknown", "Witcher 3 Remastered"),
]
