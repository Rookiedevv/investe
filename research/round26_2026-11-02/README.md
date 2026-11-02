# Round 26 (2 Nov 2026): more price drivers — aluminium, silver, bitcoin, refining cracks

**Hypothesis.** Same method as round 25. The stock's key foreign price moved last month: does the Polish stock follow next month? The signal is lagged by one day from the start, because US settlements come after the Warsaw close. Signal = driver change over the 21 sessions to the day before the month's last session; entry at the close of the next month's first session; hold 21 sessions; net of per-stock costs; vs the WIG20 TR ETF over the same dates.

**Verdict: one new paper-trade lead (Orlen after a rising diesel crack). Rest rejected.**

## Data
New Yahoo histories (2014-11 →): `ALI=F` aluminium, `SI=F` silver, `BTC-USD`, `HO=F` heating oil (diesel proxy), `RB=F` gasoline, `BZ=F` Brent. Diesel crack = HO × 42 − Brent; gasoline crack = RB × 42 − Brent (USD/bbl).

## Results (`r26a.py`, `r26b.py`)
| Stock ← driver | corr (<2021 / 2021+) | Best bucket | Verdict |
|---|---|---|---|
| Kęty ← aluminium | +0.02 (+0.10 / −0.04) | none (±1 pp) | rejected |
| KGHM ← silver | +0.05 (−0.15 / +0.20) | sign flips between periods | rejected; next-day read-through after big silver days +0.9% / 5 days, 60% right, before costs → ≈ 0 net |
| XTB ← bitcoin move / bitcoin volatility | −0.03 / +0.08 | both tails up (XTB beat the ETF most months anyway) | rejected |
| Unimot ← diesel crack | +0.04 (−0.16 / +0.17) | | rejected |
| Orlen ← Brent | −0.02 (−0.20 / +0.21) | | rejected |
| Orlen ← gasoline crack | +0.05 | | rejected |
| **Orlen ← diesel crack** | **+0.15 (+0.07 / +0.22); partial on Brent +0.16** | see below | **paper-trade lead** |

**Orlen after the diesel crack rose:**
| Crack change over the month | n | Orlen next 21 sessions vs ETF | median | beats ETF | <2021 / 2021+ | excl. 2022 |
|---|---|---|---|---|---|---|
| ≥ +3 USD/bbl | 26 | +3.0 pp (t 2.0) | +2.8 | 69% | +4.1 / +2.7 | +2.6 |
| **≥ +5 USD/bbl** | 17 | **+3.6 pp (t 2.1)** | +2.0 | **76%** | +2.8 (n=2) / +3.7 | +2.6 (n=12) |
| ≥ +8 USD/bbl | 11 | +3.4 pp | +2.0 | 82% | | +3.1 |
| ≤ −5 USD/bbl | 17 | **−2.1 pp** | −2.5 | **29%** | | |
| baseline (all months) | 142 | +0.8 pp | | 49% | | |

- The effect holds at a 10-session hold (+1.3 pp, 65%) and a 42-session hold (+2.7 pp, 71%), so it isn't one lucky window. It isn't Orlen's own momentum (+1.7 pp when Orlen was already up, +6.4 pp when it wasn't), and it isn't oil (Brent alone ≈ 0).
- Reason: the market seems to under-react to refining margins, which reach Orlen's results with a lag (the same frequency logic as the monthly-sales rules).
- Caveats: the ±5 USD/bbl threshold was picked in-sample; most cases are 2021+; n=17. That is why it is a paper-trade lead and not a trade rule.

**Rule (paper):** diesel crack (HO × 42 − Brent) up ≥ +5 USD/bbl over the 21 sessions to the day before the month's last Warsaw session → buy PKN at the close of the next month's first session, sell at the close of the 21st session after entry. ≤ −5 → avoid Orlen longs that month. `signal_now.py <YYYY-MM>` computes it after the research price files are refreshed.

**November 2026:** crack 83.6 USD/bbl on 29 Oct, −9.1 over the month → **avoid Orlen longs** (no buy).
