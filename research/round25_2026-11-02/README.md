# Round 25 (2 Nov 2026): gas and steel prices → Grupa Azoty, Police, Cognor, Stalprodukt

**Hypothesis.** The main input cost or output price of these companies moves on foreign markets first: TTF gas for the fertilizer makers, steel for the steel makers. Does last month's driver move predict the Polish stock next month (it should if the market under-reacts), or the next few days?

**Verdict: no trade rule.** One weak, illiquid lead: Stalprodukt after a big US steel-price month. Everything else is rejected.

## Data
New Yahoo histories (2014-11 →), fetched by the research workflow on 2 Nov: `HRC=F` (US hot-rolled coil futures), `MT.AS`, `VOE.VI`, `SZG.DE`, `YAR.OL`, `CF`, plus `PCE` (Police). TTF gas futures were already there (from 2017-10). Monthly tests are non-overlapping, net of per-stock costs, and compared with the WIG20 TR ETF over the same dates.

## Results
**(1) Month-end signal → next month** (`r25a.py`, `r25b.py`, `r25c.py`)
| Stock / driver | corr (both periods) | Signal | Next month vs ETF | Baseline (all months) |
|---|---|---|---|---|
| Azoty / TTF 1m | −0.19 (−0.28 / −0.13) | gas +10% | −4.9 pp, lags 69% | −2.5 pp, lags 68% |
| Police / TTF 1m | −0.19 (−0.19 / −0.22) | gas +10% | −5.3 pp, lags 77% | −3.5 pp, lags 72% |
| Cognor / HRC 1m | +0.11 after a 1-day lag fix | HRC +10% | +6.7 pp, **median −0.5, beats 50%** (n=22) | −0.2 pp |
| **Stalprodukt / HRC 1m** | +0.13 | HRC ≥ +10% (signal to the day before month end, entry next close, hold 21) | **+4.6 pp, median +2.1, beats 64%, t 1.9, n=22; <2022 +5.5, 2022+ +3.3** | −2.1 pp, beats 37% |
| Azoty, Police / Yara, CF | ≈ 0 | | | |
| Cognor / ArcelorMittal, voestalpine, Salzgitter | −0.05 to +0.16 | | | |
| KGHM, PGE / TTF (controls) | ≈ 0 | | | |

- Gas rises do hurt Azoty and Police the next month, but both stocks lag the ETF most months anyway (2017–26 decline). The gas signal adds only ~2 pp, and an XTB short after a gas spike earns +0.2% to +1.6% a month on 42–66% wins, which is no better than a deposit. Rejected.
- Cognor looked strong until the signal was lagged one day. HRC settles after the Warsaw close, so using the month-end US price would have been look-ahead. With the lag fixed, the result comes from two huge months (Feb 2021 +48, Jan 2023 +53); the median is negative. Lottery profile, rejected.
- **Stalprodukt is the only steady one.** 64–67% of months beat the ETF at thresholds of 10–12.5%, in both periods, and its own past move doesn't explain it (the placebo of Stalprodukt's own big up months: −1.0 pp). But median turnover is only about 0.1m PLN a day and the stock lags the ETF in 63% of all months, so this is a **weak paper-trade lead for small positions only**. There is no signal now: HRC was +5.3% in the 21 sessions to 29 Oct.

**(2) Daily read-through after big driver or peer days** (|z| ≥ 2, the stock not moving the same day): next 1/5/21 sessions are 41–61% right, mostly noise. Best is Stalprodukt after big ArcelorMittal days (+0.9% next day, 61%, before costs), too small after Stalprodukt's spread. Rejected.
