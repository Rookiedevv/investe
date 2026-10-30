# Round 17 (30 Oct 2026): two new data classes scraped with the browser — the KNF short-selling register and the SII Investor Sentiment Index

Both sites refuse WebFetch; the data was read through Claude in Chrome and saved here so it never has to be scraped again.

## A. KNF net-short-position register (`knf/`, `r17a.py`)
`knf/knf_hist.csv`: all 2,300 historical rows of the KNF register (positions ≥ 0.5% of share capital, 2012–2026, 67 issuers, 117 holders; `pos_date` = date the position was reached; `update_date` unreliable — bulk republications). `knf/knf_current.csv`: the 21 positions open on 30 Oct 2026. `knf/aggregate_short_interest.csv`: daily sum of open positions per issuer (a holder is dropped 90 days after its last row, since closures below 0.5% are not dated in the register). 1,861 rows map to 40 tickers with prices. Entry at the close of the session after the position date (KNF publishes the next business day), hold 21, long = eMakler costs, short = XTB CFD costs, vs WIG20 TR ETF.

| Signal | n | long vs ETF | beats | XTB short net |
|---|---|---|---|---|
| any register row | 1,693 | +0.3 pp | 47% | −3.5% |
| new position (first row of a holder-issuer episode) | 279 | +1.2 pp | 50% | −4.7% |
| increase | 680 | +0.7 pp | 48% | −4.0% |
| decrease (partial covering) | 671 | −0.3 pp | 46% | −2.9% |
| one row per issuer-week, L1 names | 1,036 | +0.6 pp | 49% | −3.8% |
| aggregate short at a 6-month high and ≥ 1% | 118 | +0.5 pp | 46% | −3.7% |
| aggregate short rose ≥ 0.5 pp in 20 sessions | 285 | +1.0 pp | 48% | −4.5% |
| aggregate short fell ≥ 0.5 pp in 20 sessions | 259 | −0.5 pp | 43% | −1.8% |
| aggregate short crosses 2% | 29 | +2.4 pp | 62% (2022+: −1.6 pp) | −5.6% |
| last position disappears (all covered) | 128 | −0.8 pp | 45% | −1.2% |

**Verdict: rejected, both ways.** Following the hedge funds' disclosed shorts loses about 3–5% a month after XTB costs (the disclosed names rise on average — CDR, PKN, KGH, LPP, PCO are the most-shorted and all went up after disclosures), and buying against them is only +1 pp vs the ETF with 50% hit rate. Short-covering (decreases, aggregate drops) does not produce bounces either. Per issuer the sign just tracks the stock's own drift (EUR, JSW, ATT negative; PKN, LPP, KGH positive), i.e. no information beyond the trend. The register stays useful only as context for the two short leads (Pepco, Eurocash): a holder adding to a short on the same day as our trigger is confirmation, not a signal.

## B. SII Investor Sentiment Index (`sii_ini.csv`, `r17b.py`, `r17b_table.csv`)
806 weekly surveys (26 May 2011 – 29 Oct 2026; bull / neutral / bear shares + WIG close). Entry at the close of the session after the survey date; forward 1 / 4 / 13 weeks of the ETF benchmark (WIG20 + 3.5%/yr before Feb 2019), minus 0.78% round trip. Signals de-duplicated to one per 4 weeks.

| Signal | n | 1w | 4w | 13w | 4w win |
|---|---|---|---|---|---|
| unconditional (all weeks) | 805 | −0.61 | −0.14 | +1.34 | 48% |
| bears ≥ 50% | 26 | −0.86 | +0.37 | +2.47 | 54% |
| bull−bear ≤ −20 pp | 25 | −0.07 | +0.95 | +1.95 | 44% |
| bull−bear 52-week z-score ≤ −1.5 | 35 | +0.42 | **+2.13** | +3.09 | 57% (t 2.3, placebo p 0.009) |
| z ≤ −1 | 65 | — | +0.64 | — | 54% |
| bull−bear ≥ 40 pp | 29 | −0.74 | −0.51 | +1.62 | 41% |
| z ≥ 1.5 | 27 | −0.78 | −0.33 | +2.24 | 48% |
| bull−bear fell ≥ 25 pp in 4 weeks | 42 | −1.28 | +0.56 | +2.49 | 51% |
| quintiles of bull−bear, 4w fwd | 162 each | q0 +0.90 · q1 −0.20 · q2 −0.62 · q3 −0.26 · q4 −0.53 | | | |

Bottom quintile beats the top in both eras (2011–18: +0.6 vs −1.4; 2019–26: +1.3 vs +0.2). Correlation of bull−bear with the next 4 weeks is −0.08 (z-score −0.11): the right sign, small.

**Verdict: a mild contrarian timing tilt, not a rule.** Only the z ≤ −1.5 cut clears the deposit bar (+2.1% in 4 weeks, median +1.3%); z ≤ −1 and the raw level do not, and the mean leans on 2020 and 2026. Use: when the SII bull−bear reading drops more than 1.5 standard deviations below its one-year average, do not sit in cash on the ETF leg that month; never as a standalone trade. Bullish extremes do not predict declines, so there is nothing to short.

## Still unreachable
Structured tender-offer (wezwania) list; developers' quarterly flat-sales tables (one PAP table per quarter on strefainwestorow) — judged too costly for the expected edge.
