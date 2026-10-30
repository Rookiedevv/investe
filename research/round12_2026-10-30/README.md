# Round 12 (30 Oct 2026): results drift beyond pre-session filings, index changes, ABB, turn of month, sector read-through, drift-rule design

All results are net of costs (L1 1%, L2 1.5%, thin 2.5%; XTB shorts ≈ 0.96%) and compared with the WIG20 total-return ETF over the same dates ("vs ETF"). "Beats" = share of trades that beat the ETF. "Excess" = vs-ETF result minus a random 21-session hold of the same stock.

Data: `cal_timing.py` — 2,559 results/preliminary filings for 60 companies with the ESPI timing (before 09:00 / after the session / during / unknown), compacted from `claude/results_calendar.csv`. Prices from `data/prices` and `research/prices` (41 of the 60 companies had prices; the missing ones — 1AT, DVL, ATT, TOR, UNI, ERB, TXT, WPL, GPW, BFT, ALL, TAR, VOT, WTN — were added to `research/prices_tickers.txt` for the next fetch).

## A. Results drift by filing time (`r12a.py`, trades in `r12a_trades.csv`)
First-news filings only (no earlier release of the same quarter within 30 sessions). Reaction = the stock's close-to-close move minus WIG20 on the reaction day: the filing day for pre-session and during-session filings, the next session for after-session filings. Entry at the reaction-day close, hold 21 sessions.

| Filing time | Reaction +3–6%, L1 | n | vs ETF | Beats | <2022 / 2022+ | Excess |
|---|---|---|---|---|---|---|
| **Before 09:00 (live rule)** | | 40 | **+5.5 pp** | **70%** | +7.3 / +3.8 | +5.1 |
| After the session → next-day entry | | 57 | +0.8 pp | 42% | +0.5 / +1.1 | −0.1 |
| During the session → same-day entry | | 10 | −0.9 pp | 70% | +1.8 / −7.3 | −2.0 |
| Pooled before + after | | 97 | +2.7 pp | 54% | +3.2 / +2.2 | +2.0 |

- Reactions above +6% after any filing time: no drift. Thin names: negative in every band.
- **Verdict:** the drift exists only after pre-session filings. The filing-time window in the evening check is doing real work; after-session reports are not a signal, even with next-day entry.
- Full reports beat preliminary releases in the pooled set (+3.1 pp vs +1.8 pp), but the pre-session subset is too small to split further.
- **Negative reactions as XTB shorts** (L1, pre + after): ≤ −3%: −1.9% per trade, 47% wins (n=118); ≤ −6%: −1.3% (n=40). Bad results don't keep falling. Rejected.
- Volume on the reaction day (vs the stock's 60-day median, Yahoo volume ratios): pre-session +3–6% trades with ≥ 1.5× volume beat the ETF 77% of the time (n=30, +6.1 pp) vs 44% (n=9, +2.8 pp) with ordinary volume. Permutation p = 0.20. Suggestive, not adopted.

## B. Index promotions and demotions (`r12b.py`, 136 WIG20/mWIG40 changes 2018–26, 121 with prices)
| Trade | n | vs ETF | Beats | Note |
|---|---|---|---|---|
| Long promoted stock, announcement close → effective-date close | 65 | +3.2 pp | 62% | +7.6 pp before 2022, +0.7 pp since; **liquid names only +0.4 pp, 48% (n=27)** |
| Long promoted stock, announcement → +21 | 65 | +1.8 pp | 49% | |
| Long promoted stock after the effective date, 21 sessions | 66 | +0.8 pp | 39% | |
| Long demoted stock | 55 | −2.4 pp | 31% | lags into the effective date |
| XTB short of demoted stock, announcement → effective | 55 | +1.2% abs | 60% | +3.7% before 2022, −0.6% since; after the effective date the short loses −5.4% (they bounce) |

**Verdict:** rejected. The inclusion effect lives in thin small caps before 2022; nothing tradable in liquid names now.

## C. ABB block sales re-run (`r12b.py`, 32 launches 2020–26)
Buy at the pricing-day close, hold 21: +3.9% net, **+1.9 pp vs ETF, beats it in 50%** (t 0.9); L1 only +2.7 pp, 54%; excluding XTB and Allegro +0.3 pp. Pricing-day gaps of −3% or worse: −2.3 pp. The earlier "weak lead" does not pass the ETF bar. Rejected.

## D. Turn of month (`r12b.py`)
WIG20 TR ETF 2019–26: last 2 + first 3 sessions average +0.08%/day vs +0.04% on other days; WIG20 2011–18: −0.02% vs 0.00%. No consistent effect. Rejected.

## E. Domestic sector read-through outside banks (`r12c.py`, 311 first-reporter → later-reporter pairs)
For each sector and quarter, the first company to report (any filing time) gives a reaction; the later reporters are held from that reaction close until their own reaction day.

| Sector | Pairs | Corr(first's reaction, later's reaction) | First ≥ +3% → later reporters vs ETF |
|---|---|---|---|
| Retail (LPP, CCC, VRG, PCO, ALE, DNP, EUR, ZAB) | 93 | +0.15 | +3.0 pp, 70%, n=20 (t 1.6); first ≤ −3% → −3.3 pp |
| Utilities (PGE, TPE, ENA) | 43 | −0.19 | −2.3 pp (n=5) |
| Finance-other (KRU, GPW, XTB, PZU) | 58 | −0.33 | −1.2 pp |
| Industrial (KTY, STP, KGH, JSW, LWB, GEA, APR, CAR) | 57 | +0.06 | −0.4 pp |
| Telecom-media, IT, construction | 14–28 each | ≈ 0 | nothing |
| **All sectors pooled** | 311 | −0.05 | −0.1 pp, 46%; first ≤ −3% → −0.3 pp (XTB short −1.2%) |

**Verdict:** rejected. Outside the banks there is no read-through: one company's results day says nothing about the next company's. Developers could not be tested (1AT, DVL, ATT prices missing; now requested).

## F. Design variants of the live drift rule (`r12d.py`, L1 ex XTB, pre-session, +3–6%, n=42)
| Variant | vs ETF | Beats | Note |
|---|---|---|---|
| Entry at the reaction close, hold 21 (live) | +6.4 pp | 71% | |
| Entry 1 session late | +5.8 pp | 69% | a missed signal can still be taken the next day |
| Entry 2 / 3 / 5 sessions late | +5.3 / +4.9 / +4.4 pp | 67 / 60 / 55% | edge decays slowly |
| Hold 10 / 15 | +2.6 / +3.6 pp | 60 / 55% | too short |
| Hold 30 | +7.4 pp | 74% | similar to 21; 2022+ +4.6 vs +4.5 |
| Hold 42 / 63 | +4.8 / +6.8 pp | 57 / 64% | lower per-day, more risk |
| Prior 6-month return vs WIG20 > 0 | +9.1 pp | 82% (n=22) | vs +3.1 pp, 58% when ≤ 0; permutation p 0.04 — **but fades on the wider band (+2–6%: p 0.16) and with L2 names (p 0.3)**; weak tilt, not a filter |
| Prior 1-month return ≤ 0 | +7.2 pp | 74% | n=23; no clear pattern |
| More than 20% below the 52-week high | +8.0 pp | 82% | n=11 |
| WIG20 above / below its 200-day average | +6.8 / +5.8 pp | 67 / 78% | regime doesn't matter |
| Strong close (top third of the day's range) | +7.2 pp | 67% | vs +5.0 pp, 80% otherwise; nothing |

**Takeaways for the evening check and the app:** keep entry at the reaction close and the 21-session hold; a signal found a day late is still worth taking; prefer (but don't require) names that beat WIG20 over the previous six months.

## G. Banks: no drift after their own results (`r12e.py`, 197 first-news bank filings 2021–26 from `claude/bank_events.csv`, 9 banks)
Banks file before the session by habit (PKO, Pekao and Alior at night; the rest 07:00–08:50), so nearly all of them qualify for the live rule's filing window.

| Pre-session bank filing, reaction vs WIG20 | n | vs ETF | Beats | 2021–22 / 2023+ |
|---|---|---|---|---|
| **+3% to +6%** | 23 | **+0.4 pp** | 52% | +0.2 / +0.6 |
| +2% to +6% | 36 | +0.1 pp | 50% | −0.1 / +0.3 |
| above +6% | 5 | +1.7 pp | 60% | |
| +1% to +3% | 32 | +0.9 pp | 50% | |
| below −3% | 18 | +2.3 pp | 50% | bad bank results don't keep falling either |

Correlation between the reaction and the next 21 sessions vs the ETF: −0.03. Per bank, only Alior (+6.0 pp, n=6) and mBank (+4.5 pp, n=4) are positive after a ≥ +2% reaction; BNP is −8.1 pp (n=5).

The six bank filings that happened to be in the round-9 calendar (mostly 2021: Alior +14.6 pp, mBank +21.2 pp) made banks look as good as the rest; the full 2021–26 set says otherwise. Excluding banks from the round-9 pre-session set changes nothing for the others: +5.5 pp, 71% (n=34); excluding banks and XTB: **+6.3 pp, 75% (n=32)**.

**Recommendation:** the evening results-drift check should skip the nine banks (PKO, PEO, MBK, ALR, ING, MIL, EBP, BNP, BHW) as it skips XTB. Bank results days stay covered by the separate bank read-through rule (first reporter → later reporters), which is a different mechanism.

## Summary
- Rejected: after-session and during-session drift, banks' own-results drift (+0.4 pp, n=23 → skip banks in the evening check), negative-reaction shorts, index promotions/demotions (long and short), ABB buys, turn of month, non-bank sector read-through.
- Kept: the pre-session drift rule as it is, with two soft notes (late entry is fine; six-month momentum and high reaction-day volume tilt the odds, neither robust enough to be a filter).
