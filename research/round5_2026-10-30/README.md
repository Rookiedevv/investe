# Round 5 (tested 30 Oct 2026): macro and calendar drivers

**Benchmark:** every result is net of costs and compared, over the same dates, with the WIG20 total-return ETF (ETFBW20TR from 2019; WIG20 + 3.5%/yr dividends before that), with eMakler fees on the ETF too.
- **"Beats ETF"** is the share of trades or months that did better than the ETF.
- **Costs:** 1% on stock baskets, about 0.1% on an FW20 short.
- **Signals:** month-end signals, held 1 month, unless stated otherwise.
- **Scripts:** `r5.py`, `r5b.py`. Run them from `research/`.

| Idea | Result | Verdict |
|---|---|---|
| **Zloty moves** (USD/PLN or EUR/PLN ±2–3% over a month): next-month WIG20 ETF, or exporters KGH/KTY/JSW vs ETF | Exporters after a weaker PLN *lag* (−1.4 pp, beat ETF 37%). After a stronger PLN, +1.6–2.1 pp, but n=23–36 and weaker after 2019. EUR/PLN samples are tiny. | Rejected |
| **WIG20 lagging DAX / S&P 500 by >3–5 pp in a month** | WIG20 doesn't catch up. It keeps lagging slightly, but an FW20 short only makes +0.2–0.5% (54% wins) and the sign flips between periods. Banks −1.2 pp. | Rejected |
| **VIX spike (>25/30) then a 20–30% retreat**, buy WIG20 ETF or banks for 21 sessions | ETF +0.1 to +1.6 pp vs deposit, 50–63%; banks lag the ETF | Rejected |
| **Sector rotation**: hold the best sector (banks / utilities / commodities / consumer / tech-gaming / financials / construction) by 3-month return | +2.5 pp vs ETF per month (t 3.4, both periods), but beats the ETF in only **54%** of months. 6-month and 1-month versions are weaker; bottom-sector reversal fails | Rejected: same weakness as the 52-week-high rule (average driven by a minority of months) |
| **Turn of the year**: liquid mid caps, buy 31 Dec, sell end of January | +2.9 pp vs ETF, beat it in 9 of 12 years (2015–2026); smaller names 10 of 12 (+3.4 pp) | **Not an edge on its own**: the same mid caps beat the ETF by about +1 pp in an average month (survivorship: today's liquid names). January is the best month (+2.9), December the worst (−1.3, 36%), consistent with tax-loss selling, but n=12 years |

**Conclusion:** none of these pass. Universe-based tests on today's liquid names are inflated by survivorship (mid caps "beat" the ETF in most months), which makes the event-driven rules (results drift, read-through, Biedronka→Dino, Asbis monthly sales) more trustworthy than price- or macro-based ones.
