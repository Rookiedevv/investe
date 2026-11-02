# Round 27 (2 Nov 2026): periodic-report date changes (postponed / brought forward)

**Hypothesis.** A company that moves its results date later is buying time for bad news (avoid / XTB short); one that moves it earlier has good news. Tested three ways: hold 21 sessions from the first tradable price after the notice; the move from the notice to the report; and the report-day reaction. All vs the WIG20 TR ETF over the same dates.

**Verdict: rejected.** The postponement effect is mostly JSW, and the reports themselves don't disappoint.

## Data
`dates_A.csv` (2016–mid 2021) and `dates_B.csv` (mid 2021–2026): 74 date-change notices, 75 rows, at 20 companies. 43 moved later, 26 earlier, 5 unknown, 8 during COVID. Coverage is partial and leans to banks, utilities and JSW (mBank 12, JSW 9, Orange 6, Enea 6). Most other names got no hits, and a missing hit doesn't mean there was no change. Times are often unknown, so those notices are entered at the next session's close.

## Results (21 sessions)
| Group | n | vs ETF | median | beats ETF | notice→report | report-day reaction | XTB short |
|---|---|---|---|---|---|---|---|
| later (ex COVID) | 35 | −2.8 pp | −3.9 | 31% | −1.5 | **+1.1 (negative 43%)** | +0.6%, 60% win |
| later, liquid | 31 | −3.9 pp (t −2.0) | −4.3 | 26% | −1.7 | +1.0 | +1.6%, 58% |
| later, JSW only | 9 | −6.7 pp | | | | | |
| later, excl. JSW | 26 | −1.5 pp | | 35% | | | |
| later, excl. JSW and banks | 16 | +0.4 pp | | | | | |
| later, delay ≥ 14 days | 13 | −4.3 pp | −2.8 | 31% | −4.5 | +0.0 | +1.3%, 69% |
| earlier (ex COVID) | 25 | −0.8 pp | +0.6 | 52% | −0.8 | +0.1 (negative 68%) | |
| COVID-period changes | 8 | +1.4 pp | −3.3 | 38% | | | |

- The idea fails at its core: after a postponement the report-day reaction is positive on average, not a disappointment. The lag after postponements comes from JSW, whose stock fell through 2022–26 while it postponed nine times. Without JSW and the banks it is +0.4 pp.
- The XTB short after a postponement earns +0.6% to +1.6% per month, about the same as a deposit. Bringing a date forward means nothing.
- Revisit only with complete data (every company's annual schedule and change notices, which would need an ESPI archive scrape).
