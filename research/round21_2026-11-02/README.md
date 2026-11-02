# Round 21 (2 Nov 2026): share buyback announcements → buy and hold 1 month

**Hypothesis.** When a company announces a buyback (skup akcji własnych), management is signalling that the shares are cheap and will be buying them itself. Abroad, shares tend to keep outperforming after buyback news. Test: buy at the first price you could actually trade after the news, hold 21 sessions, after per-stock costs, and compare with the WIG20 TR ETF over the same dates and with random 21-session holds of the same stock.

**Verdict: rejected.** On GPW, buyback news has no tradable one-month edge. The few large wins come from outliers, mostly Mercator in the 2020 glove boom.

## Data
- `seed_known.csv` (36 events, from the project's `abb_buybacks.csv`) plus `buybacks_A/B/C.csv` (106 events collected from ESPI copies on parkiet/bankier, biznesradar, strefainwestorow and company pages). Total 138 events at 33 companies, 2014–2026, with prices for all of them.
- Event types: board proposal 32, GM authorization 25, programme start/tranche 19, tender (invitation to sell at a fixed price) 51, incentive-only 11.
- Entry price: news before 09:00 → that day's open; during the session → that day's close; after 17:05 → next open; time unknown → next close (conservative).
- Caveats: many release times come from news articles rather than the ESPI filing; 23 rows have uncertain dates; the "none found" check was light for about 20 companies (Dino, Budimex, Orange, GPW and others got no dedicated search; most of them have no buyback history anyway).

## Results (21 sessions, net of costs, vs WIG20 TR ETF same dates)
| Group | n | mean vs ETF | median | beats ETF | <2022 | 2022+ |
|---|---|---|---|---|---|---|
| all excl. incentive | 127 | +1.4 pp | −1.8 | 42% | +3.8 | −1.0 |
| same, excl. Mercator | 116 | −0.7 pp | −1.4 | 41% | | |
| board proposal | 32 | −2.6 | −4.0 | 34% | −4.9 | +1.9 |
| GM authorization | 25 | +2.3 | +1.8 | 52% | +4.5 | −2.3 |
| programme start / tranche | 19 | −1.7 | −1.1 | 47% | −3.1 | −1.2 |
| tender | 51 | +4.5 | −0.7 | 39% | +14.0 | −1.6 |
| incentive only | 11 | −2.1 | −1.1 | 36% | | −2.1 |
| liquid (> 3m PLN/day), excl. Mercator | 36 | +0.7 | −0.2 | 50% | | +0.1 |
| size ≥ 3% of shares | 66 | +2.6 | −3.4 | 41% | +6.0 | −0.9 |
| first news of a programme (no buyback news in 180 days) | 76 | +0.6 | −1.4 | 43% | | |
| certain dates only | 104 | −0.8 | −2.9 | 39% | | |

- With a 10-session hold everything is about zero (all −0.5 pp, 41%). The 42-session means look large only because of Mercator 2020 (medians −1 to −2.5, beats 38–45%).
- The news is priced on the day: the average reaction from the last close to the entry price is +2.1 pp vs WIG20. After that there is no drift.
- Trimmed means (5% each side): all −0.8 pp, tenders +0.0 pp.

## Side test: after a tender closes
A fixed-price tender puts a temporary floor under the price. Measured from 10 to 31 sessions after the tender news (roughly after the offer window), excluding Mercator: median −3.1 pp vs the ETF and 61% lag it (n=45), but the mean is +0.1 pp. Most of these names are illiquid and not shortable on XTB. The liquid ones (PCO ×2, CAR, TEN, ACP, CPS, ALE, KRU, WPL; n=10) are mixed: Pepco −13/−12, but KRU +6.5 and ALE +2.3. **Not a lead.** Revisit only if more liquid tenders accumulate. Pepco's pattern, a fall after its tender windows, is worth watching at the next Pepco tender.

## Files
`r21a.py` (run with `HOLD=10/21/42`), `r21a_trades_h21.csv` (per-event results), event CSVs above.
