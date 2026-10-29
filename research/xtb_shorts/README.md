# XTB shorts from existing avoid signals (tested 29 Oct 2026)

**Question:** several earlier findings were "avoid" signals, i.e. a stock tends to fall after an event. When they were found, only a cash account was available, so they could not be traded. With XTB CFDs they can be shorted. Do they pay as shorts?

## Method

**Prices:** Yahoo daily, adjusted for dividends. These files are research-only and are not loaded into Supabase. They are in `research/prices/`, fetched by the `research-prices` workflow; edit `research/prices_tickers.txt` to add tickers.

**Benchmark:** WIG20.

**Trade:** short at the first close that can trade the news, then cover after 21 sessions. Trades in the same stock do not overlap.

**Costs (XTB):**
- 0.30% markup on each side;
- per-stock spread and price impact for a 20k zł order (tiers from `claude/stock_costs.csv`);
- short swap of about 0.7% a year.

The total round trip is about 0.8% for liquid names and up to about 2.5% for Eurocash.

**Comparison:** random-day shorts in the same stock, net of the same costs.

## Results

| Hypothesis (source avoid signal) | n | Short net | Wins | t | <2022 / 2022+ | Random shorts | Verdict |
|---|---|---|---|---|---|---|---|
| **Pepco after an Inditex/H&M results day ≤ −5%**, short at the Warsaw close that day | 11 | **+7.0%** | 82% | 2.5 | +13.2% (1) / +6.3% (10) | −1.5% | **Short lead** |
| same, short at the next close | 11 | +5.2% | 82% | 1.9 | — | −1.5% | |
| same, threshold ≤ −3% | 17 | +4.1% | 71% | 1.7 | — | −1.5% | |
| Control: LPP after the same days | 17 | −3.1% | 35% | — | — | −3.3% | No effect, so the effect is specific to Pepco |
| **Eurocash after a Dino results reaction ≤ −3%** | 10 | **+4.6%** | 80% | 2.8 | +6.3% (2) / +4.2% (8) | −2.0% | **Short lead, but illiquid** |
| Eurocash after its own bad report (≤ −3%) | 15 | −1.5% | 40% | — | — | −2.0% | Rejected as a short |
| Polimex contract ≥ 10% of revenue AND reaction ≥ +3% | 10 | +8.1% | 60% | 2.2 | +14.2% (4) / +4.1% (6) | −2.6% | Weak lead (two filters; revenue approximate) |
| Polimex contract, reaction ≥ +3% (any size) | 23 | +3.1% | 48% | 1.0 | +9.2% / −0.7% | −2.6% | Rejected |
| Gaming launches 2021+, short the next month | 13 | +6.9% | 69% | 2.0 | — | — | Lead, but mostly illiquid names |
| same, launch day ≥ +3% | 6 | +11.1% | 83% | 3.1 | — | — | Too few trades |
| Gaming launches, CDR + 11B only, all years | 16 | −0.3% | 62% | — | −8.3% / +5.9% | — | Rejected in all years: Frostpunk 2018 lost −79% |
| Index demotion, short from announcement to effective date | 55 | +0.3% | 62% | — | +2.1% / −1.1% | — | Rejected: the −2.4 pp relative lag is too small for an outright short |
| Index promotion, short after effective date | 68 | −6.0% | 50% | — | — | — | Rejected |
| Big down day (> 2.5 SD below WIG20) → short, 22 liquid stocks | 300 | **−3.6%** | 40% | −4.4 | — | — | Rejected: big down days bounce |
| Rainbow Tours big down day | 15 | +6.2% | 67% | 1.4 | +15.9% / −0.4% | — | Rejected: the gain is all pre-2022 |
| **JSW rule re-run on Yahoo data** (2.5 SD below WIG20) | 17–20 | +0.5% to +0.9% | ~54% | — | — | — | **Does not replicate the Stooq result (+4.0%). Needs reconciling.** |

## Notes

**Pepco**
- Pepco barely moves on the peer's day itself (median 0%), then drifts down over the next month in 9 of 11 cases. The market prices the read-through slowly.
- 10 of the 11 trades are from 2022 or later, when Pepco was in a long decline. Random shorts still lost −1.5%, so the decline alone does not explain the result.
- Holding 10 sessions gives +3.6% and holding 42 gives +1.9%; 21 sessions is the best hold.
- XTB lists a Pepco CFD.

**Eurocash**
- The stock fell in 9 of the 10 windows.
- Turnover is about 0.9m zł a day, so costs are about 2.5% a round trip, and it is not confirmed that an XTB short is available.
- Eurocash is now in sWIG80.

**JSW rule**
- On Yahoo data for 2015–26 the JSW rule gives +0.9% a trade (n=20) with a rolling 250-day SD, and −2.7% with a full-sample SD.
- The stored rule (+4.0%, n=33, Stooq data 2011–26, benchmark WIG) needs to be re-checked against the exact original definition before it is trusted.

Script: `research/xtb_shorts/test_shorts.py`; events: `events.py`, `index_changes.csv`.
