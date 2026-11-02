# Round 22 (2 Nov 2026): financial investors crossing 5/10/15% → follow them for 1 month

**Hypothesis.** When an OFE, a TFI or a foreign asset manager crosses a disclosure threshold, informed money is moving. Rule tested: buy at the first price tradable after the company publishes the notice (upward crossing), or avoid / short on XTB (downward crossing), and hold 21 sessions. Results are after per-stock costs and compared with the WIG20 TR ETF over the same dates.

**Verdict: no edge in the sample, but the sample is incomplete — inconclusive, not a clean rejection.**

## Data
`stakes_A/B/C.csv`: 82 notices at 33 companies, 2016–26 (45 OFE, 20 TFI, 11 foreign asset managers, 6 other financial). Web search finds only a fraction of the real notices: 1–3 searches per company, and many notices keep the numbers only in a PDF attachment. 14 rows are fund mergers (Aviva→Allianz, NN→Generali) and are excluded from the tests. 9 rows have an unknown direction. Many publication times are unknown, so those entries use the next close (conservative).

## Results (21 sessions, market/unknown cause only)
| Group | n | net | vs ETF | median | beats ETF | XTB short |
|---|---|---|---|---|---|---|
| upward crossing | 29 | −0.2% | +1.1 pp | +0.4 | 52% | −3.1%, 55% win |
| upward, liquid (> 3m PLN/day) | 13 | +1.1% | +2.8 pp | +0.8 | 62% | |
| upward, stock already +5% vs WIG20 in prior month | 11 | +3.6% | +4.4 pp | +2.5 | 64% | |
| downward crossing | 23 | +0.1% | −0.0 pp | −1.3 | 39% | −3.6%, 43% win |
| downward, OFE only | 10 | −2.9% | −3.5 pp | −2.5 | 30% | −0.2% |
| fund-merger crossings (placebo) | 14 | −1.2% | +0.2 pp | −1.0 | 43% | |

- Nothing reaches t = 2. The reaction on the notice day is about zero (+0.3 pp): the fund's buying shows up in the month before the notice (+4 pp vs WIG20 for upward crossings), not after it.
- Weak hints only, none of them a rule: liquid upward crossings, upward crossings in stocks already rising (momentum overlap, compare the round 4 52-week-high test), and OFEs dropping below 5% (avoid, n=10).

## What a proper test would need
A complete list of notices. Each company's ESPI archive (stockwatch, biznesradar, or the company's IR page) would have to be scraped in a real browser, the same way the KNF short register was in round 17, and the attachments read for direction and percentages. That means roughly 40 companies × 10 years.
