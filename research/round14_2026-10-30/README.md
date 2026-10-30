# Round 14 (30 Oct 2026): quarterly revenue acceleration (the Asbis / car-parts logic on quarterly reports)

**Idea:** the two best live rules use *monthly* sales acceleration (this month's y/y minus the average y/y of the previous three months). Does the same logic work on *quarterly* reports, which every company publishes?

**Data (`revenue/*.csv`):** quarterly revenue ('Przychody ze sprzedaży') from biznesradar's quarterly income statements for 9 liquid companies — Allegro, Budimex, Dino, KGHM, Kęty, LPP, Orlen, PGE, XTB — 2014–2026 (266–295 quarter-filings). The same pages for CD Projekt, Asseco, Tauron, Kruk, Inter Cars and others came back as annual tables through the fetch tool; Pepco reports half-years only. Coverage is therefore partial. LPP's fiscal year moved in 2020, so its quarters are offset by a month (results are shown with and without LPP).

**Method (`r14a.py`):** acc = y/y revenue growth of the quarter minus the mean y/y of the previous three quarters, known at the quarter's first-news filing (date and timing from `round12_2026-10-30/cal_timing.py`). Entry at the reaction-day close (filing day for pre-session filings, next day for after-session), hold 21 and 63 sessions, costs 1–1.5%, compared with the WIG20 TR ETF over the same dates.

| Signal (ex LPP, n=266) | n | 21 sessions vs ETF | Beats | 63 sessions vs ETF | Beats |
|---|---|---|---|---|---|
| all quarter-filings | 266 | +1.1 pp | 52% | +2.7 pp | 51% |
| **acceleration > 0** | 134 | **+1.1 pp** | **46%** | +2.8 pp | 51% |
| acceleration > 5 pp | 102 | +1.3 pp | 48% | +4.1 pp | 52% |
| acceleration > 10 pp | 74 | +0.9 pp | 45% | +4.4 pp | 51% |
| acceleration ≤ 0 | 132 | +1.2 pp | 57% | +2.7 pp | 51% |
| acceleration < −10 pp | 79 | +1.9 pp | 56% | +1.9 pp | 49% |
| y/y growth > 10% | 146 | +1.5 pp | 52% | +3.6 pp | 54% |
| acc > 0 and positive reaction | 59 | +2.2 pp | 54% (t 1.6) | +5.7 pp | 54% |
| acc > 0 and reaction ≥ +3% | 30 | +1.5 pp | 50% | +4.5 pp | 50% |

Correlation of acceleration with the reaction-day move: −0.01; with the next 21 sessions vs the ETF: 0.05; with the next 63 sessions: 0.21.

Pre-session filings only (n=100): acceleration > 10 pp → +2.3 pp over 21 sessions but only 42% beat the ETF (+10.4 pp over 63 sessions, 58%); **acceleration < −10 pp → −2.6 pp over 21 sessions, 39%, and −6.2 pp over 63 sessions, 32% (n=28)**.

**Verdict:** rejected as a one-month rule — quarterly revenue acceleration has no relation to the next month (accelerating and decelerating quarters both earn about +1 pp vs the ETF, and accelerating ones beat it less often). There is a slow fundamental-momentum tilt over three months (corr 0.21, +4 pp for strong acceleration) and a weak avoid signal for sharply decelerating revenue after a pre-session report (n=28). The monthly-sales edge (Asbis, car parts) comes from the *frequency* of the data — a month-by-month read on the trend the market under-reacts to — which quarterly reports, fully digested on the day, do not provide. Not adopted; a broader test would need quarterly data for more companies than the fetch route delivers.
