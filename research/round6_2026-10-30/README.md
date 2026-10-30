# Round 6 (tested 30 Oct 2026): foreign peer results → Polish stocks

**Data:** 29 foreign peers (Yahoo, `research/prices_foreign/`, 2014–2026; EA failed to download).

**Results days:** proxied as each peer's largest move against its home index (S&P 500 or DAX) in each quarter, counted only if larger than 2× its normal daily move. Earnings days are usually the biggest move of the quarter.

**Trades:**
- Entry at the Warsaw close on the peer's reaction day, or the day after.
- Hold 21 sessions.
- Longs are compared with the WIG20 total-return ETF over the same dates, after costs.
- Shorts are XTB, in absolute terms.

**Scripts:** `r6.py`, `r6b.py`. Run them from `research/`.

| Peer group → Polish stock | Peer jumps → buy (vs ETF) | Peer drops → XTB short | Verdict |
|---|---|---|---|
| Gaming (Take-Two, Ubisoft, Embracer) → CDR, 11B, TEN, PLW, CIG | +1.0 pp, 52% | −2.7 to −3.5%, 39–43% wins | Rejected |
| E-commerce (Amazon, Zalando) → Allegro | −2.6 to −3.2 pp | ≈ 0 | Rejected |
| Copper (Freeport, Antofagasta) → KGHM | +2.0 to +2.8 pp, median ≈ 0, 47–51% | −1.8 to +0.1% | Rejected |
| Oil (BP, Shell, OMV) → Orlen | +0.1 pp | −3.2% | Rejected |
| CFD brokers (IG, Plus500, CMC) → XTB | +5.6 pp, 59%, but XTB's own random month is +1.7 pp and **without 2020 it's +1.5 pp, 54%** | ≈ 0 | Rejected (COVID-year artefact) |
| Debt collectors (Intrum, Hoist) → Kruk | ≈ 0 | **−5 to −6% (Kruk *rises* when they fall)** | Short rejected. Mirror long: **Kruk after an Intrum/Hoist drop +2.5 pp vs ETF, 59%, n=39, both periods; Kruk's random month +0.8 pp (53%) → excess +1.7 pp.** Weak lead, below the bar |
| CEE / parent banks (Erste, OTP, RBI, Komerční, ING, Santander, BNP, UniCredit, Commerzbank) → Polish banks | +0.3 pp, 50% | −2.0%, 45% | Rejected |
| LKQ → Inter Cars, Auto Partner | +2.2 to +2.6 pp, median ≈ 0 | −2.8% | Rejected |

**Conclusion:** foreign results days don't move Polish peers in a tradable way. The same-day link is weak (correlation 0.13–0.18) and nothing drifts afterwards. The one earlier success (Pepco after Inditex/H&M) remains an exception: there the foreign peer is a direct competitor in the same stores and markets.
