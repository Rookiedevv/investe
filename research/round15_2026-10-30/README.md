# Round 15 (30 Oct 2026): Polish bond yields vs banks; web sources re-tried

## A. 10-year yield moves → banks / utilities / WIG20 next month (`r15a.py`, FRED IRLTLT01PLM156N monthly average 2010–26, `pl10y.csv`)
Signal = change in the 10-year yield over the past 3 months, known at the end of the month (the monthly average is published a few days later, so a 2-month lag is also shown). Trade = equal-weight basket next month, compared with the WIG20 TR ETF.

| 3-month yield change (lag 1) | Months | Banks next month | vs ETF | Win |
|---|---|---|---|---|
| **up more than 0.5 pp** | 14 | **−3.0%** | **−2.2 pp** | 21% |
| 0 to +0.5 pp | 30 | +2.8% | +2.1 pp | 73% |
| −0.5 to 0 pp | 38 | +3.0% | +0.6 pp | 47% |
| down more than 0.5 pp | 11 | +2.2% | +2.3 pp | 64% |

Correlation of the 3-month yield change with next month's bank return: −0.15 (lag 1), −0.19 (lag 2). Utilities and WIG20: no relation. With the 2-month lag the "sharp rise" cell stays negative (−2.0 pp, 31%), the other cells reshuffle.

**Verdict:** one usable cell — after a bond sell-off (10-year yield up more than 50 bp over three months) banks lag the ETF the following month in 11 of 14 cases (mostly 2021–22, plus 2013 and 2026). It is an **avoid filter for bank longs**, not a trade (an XTB short of the basket would net ~+2% at best with 14 cases). Not monotonic in the middle bins, so not a factor. Logged, not adopted.

## B. Web sources (30 Oct 2026)
- KNF short-selling register (rss.knf.gov.pl): reachable but returns an error page to the fetch tool (JavaScript/session-based); current and historical lists both empty. Needs a real browser.
- SII Investor Sentiment Index (weekly bull/bear since 2011, Excel history on sii.org.pl): the site refuses the fetch tool.
- Tender offers (wezwania): no structured public list found; biznesradar's news topic pages (25 pages) only give partial announcements without prices. Collecting 2018–26 tenders by hand would be a multi-hour job with brittle sources.
- biznesradar quarterly income statements: parse for some companies only (used in round 14).
