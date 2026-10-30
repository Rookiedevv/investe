# Round 11 (30 Oct 2026): more company monthly publishers? XTB short leads re-run

## Who else publishes monthly sales on GPW/NewConnect (search of ESPI reports, Oct 2026)
- **Liquid and already tested:** Asbis (monthly revenue), Inter Cars and Auto Partner (monthly sales). Rainbow Tours (monthly sales) was weak.
- **Monthly publishers, all too thin to trade** (well under 1m zł/day): Bio Planet, Artifex Mundi, TenderHut, Kolejkowo, Woodpecker, Esotiq (historical).
- **Quarterly preliminary sales / operating updates:** LPP, Pepco, Answear, Modivo, Asseco Poland, ASEE, Cormay, Sunex, Selvita and others. These are already covered by the results-drift rule when filed before the session.
- **Stopped publishing monthly:** VRG (after June 2024).

**Conclusion:** there are no further liquid monthly publishers to add. The company-data edge on GPW is concentrated in the names already used.

## XTB short leads re-run (`../xtb_shorts/test_shorts.py`, Yahoo data, XTB costs, random-short placebo)
| Lead | n | Short net | Wins | t | Random shorts, same stock | <2022 / 2022+ |
|---|---|---|---|---|---|---|
| Pepco after an Inditex/H&M day ≤ −5%, short at the same-day close | 11 | +7.0% | 82% | 2.5 | −1.5% | +13.2 (1) / +6.3 (10) |
| Pepco, same, ≤ −3% | 17 | +4.1% | 71% | 1.7 | −1.5% | +7.7 (2) / +3.6 (15) |
| Eurocash after a Dino results reaction ≤ −3% | 10 | +4.6% | 80% | 2.8 | −2.0% | +6.3 (2) / +4.2 (8) |
| Polimex contract ≥ 10% of revenue and pop ≥ +3% | 10 | +8.1% | 60% | 2.2 | −2.6% | +14.2 (4) / +4.1 (6) |
| Gaming launch month, 2021+ | 13 | +6.9% | 69% | 2.0 | — | mostly illiquid names |

Unchanged from 29 Oct: Pepco and Eurocash remain the only short leads, both small n and mostly post-2022. The JSW big-down-day rule does not replicate on Yahoo data (+0.5 to +0.9%), so it is downgraded to rejected.
