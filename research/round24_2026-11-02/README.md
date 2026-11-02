# Round 24 (2 Nov 2026): dividend proposal surprise

**Hypothesis.** A board proposing a much bigger dividend than last year (or a first dividend) is a confidence signal → buy; a cut or a skipped dividend → avoid or XTB-short. Each trade enters at the first price tradable after the proposal, holds 21 sessions, pays per-stock costs, and is compared with the WIG20 TR ETF over the same dates.

**Verdict: the surprise rule is rejected.** One weak side-observation: when the proposed dividend is ≥ 8% of the price, the stock beats the ETF over 21 sessions. It disappears at 10 and 42 sessions, so it is not a rule.

## Data
`divs_A/B/C.csv` hold dividend history for 44 companies (amounts per fiscal year from biznesradar). Of these, 179 proposals have a dated announcement, almost all from fiscal years 2017–2025. Dates are mostly news-article dates and times are mostly unknown, so those entries use the next session's close (conservative). Coverage of 2013–2017 is poor.

## Results (21 sessions, vs WIG20 TR ETF same dates)
| Group | n | vs ETF | median | beats ETF | XTB short |
|---|---|---|---|---|---|
| all proposals | 178 | +0.1 pp | −0.4 | 49% | −3.6% |
| raise ≥ 20% | 37 | −0.5 | −1.0 | 49% | |
| raise ≥ 50% | 18 | −2.1 | −4.1 | 39% | |
| first dividend | 21 | −0.2 | +1.5 | 57% | |
| raise ≥ 20% or first | 58 | −0.4 | +0.8 | 52% | |
| cut ≥ 20% | 18 | +0.1 | −0.2 | 50% | −4.2%, 39% win |
| skipped | 17 | −1.7 | −3.3 | 35% | −2.9%, 47% win |
| cut or skipped, liquid | 25 | −2.9 | −3.9 | 32% (t −2.0) | −1.5%, 48% win |
| **proposed yield ≥ 8%** | 29 | **+2.5** | +1.7 | **69% (t 2.1)** | |
| proposed yield ≥ 6% / ≥ 9% / ≥ 10% | 57 / 17 / 11 | +2.1 / +3.2 / +3.7 | | 65% / 76% / 73% | |

- The size of the change carries no information. The reaction on the day (+2.1 pp after raises) is the whole move, and big raises (≥ 50%) even lag afterwards.
- Cuts and skipped dividends at liquid names lag the ETF by about 3 pp (32% beat it, n=25). That would be a weak avoid filter, but the XTB short still loses because of costs and swap.
- **High-yield proposals:** +2.5 pp at 21 sessions, but only +0.7 pp at 10 and +0.3 pp at 42 sessions. That peak only at 21 looks like noise, or like dividend-season buying in banks and Kęty during the 2024–26 bull market (11 of 29 events are banks). Round 4 already rejected buying in the run-up to the ex-dividend date. Not a rule; worth re-checking if a cleaner dataset with exact ESPI times is ever built.
