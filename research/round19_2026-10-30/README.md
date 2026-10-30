# Round 19 (30 Oct 2026): new data classes — CHF/PLN, EPOL, coal and gas futures, IPO list, MSCI review lists

New series fetched by the research-prices workflow into `research/prices_foreign/` (CHFPLN=X, EPOL, MTF=F Rotterdam coal, TTF=F gas) and `research/prices/` (IPO names). `msci_changes.csv` = every Polish addition/deletion in the MSCI Standard and Small Cap indexes 2015–2026, read from MSCI's public review PDFs (`MSCI_<Mon><YY>_STPublicList.pdf` / `_SCPublicList.pdf`); 86 events, 64 with prices.

## A. Combinations of existing data (`r19a.py`) — rejected
Pre-session drift signals × KNF short interest: with an open short +5.3 pp vs ETF, without +5.2 pp — short interest adds nothing. × analyst reaction within 5 sessions: too few overlaps. Negative pre-session reactions ≤ −3% as contrarian longs: +0.05 pp. WIG20 short-horizon patterns re-costed for the XTB W20 CFD (0.05% + 0.03%/day): the best (day ≤ −2%, hold 5) is +0.38% net, 60%, and most are ±0.2% — nothing worth a leveraged instrument.

## B. CHF/PLN → CHF-mortgage banks (`r19b.py`, `r19c.py`)
Monthly CHF moves: no relation (corr −0.03 to −0.06). Daily jump ≥ 1.5% (23 non-overlapping days 2015–26) → XTB short of **MIL +1.8% net / 5 sessions (63%), +1.9% / 21 (58%); MBK +1.6% / 5 (53%)** — but ≥ 1.0% (n=48) gives −1.4% and ≥ 2.0% (n=8) loses, so the result lives on one threshold. **Weak short lead**, not a rule.

## C. EPOL after the Warsaw close → next-day WIG20 (`r19b.py`, `r19c.py`)
EPOL's day return minus WIG20's (in USD) ≈ what Polish stocks did 17:00–22:00. corr with next-day WIG20 close-to-close 0.13 (n=2,918); resid ≥ +1.5% → +0.34%, ≤ −1.5% → −0.28%. **All of it is in the FW20 opening gap** (corr with the gap 0.175, with open→close 0.03; open→close after resid ≥ +1.5%: +0.11%, 53%). Not tradable at 08:45. Rejected — and a useful negative: overnight information is fully in the open.

## D. Coal futures → JSW / Bogdanka (`r19c.py`, month-end, non-overlapping, 2015–25)
corr(coal 1-month change, next-month stock vs ETF) +0.21 for both. Coal up > 10% → JSW +8.9 pp (beats 45%, n=20), LWB +4.7 pp (50%); coal down last month → LWB −5.2 pp, 28% beats, t −3.4 (n=61). Lottery profile for JSW (big mean, coin-flip hit rate); for LWB an avoid filter that overlaps the existing TGE-power short lead. **Tilt, not a rule.**

## E. IPOs 2015–2025 (`ipos.csv`, `r19d.py`) — rejected / data too thin
Yahoo has usable histories for only 21 of 46 listings (many start months after the debut). Post-IPO months alternate in sign (month 1 +3.4 pp, 4 −3.4, 7 +3.3, 8 −4.6, 11 −3.9); the 180-day lock-up window is +2.8 pp and the month after it −4.9 pp (33% positive, n=21) — noise with n=21 and uncertain lock-up dates.

## F. MSCI index reviews (`msci_changes.csv`, `r19e.py`, `r19f.py`) — one real lead
| Event (n with prices) | reaction day | ann+1 → effective, long vs ETF | effective close → +21, long vs ETF | XTB short from effective close, 21 |
|---|---|---|---|---|
| Standard addition (12) | +2.7% | −1.1 pp, 50% | **−7.2 pp, beats 17%** | **+3.7% net, 75%** |
| Standard deletion → Small Cap (14) | −1.9% | +2.1 pp, 50% | +0.6 pp, 43% | −4.8% |
| Small Cap addition (19) | +2.2% | −5.8 pp, 21% (short +1.6%) | +1.4 pp | −5.6% |
| Small Cap deletion (19) | −1.8% | −2.9 pp | −2.7 pp | −0.8% |

**Standard-index additions reverse after the flow day.** Short at the effective-date close, cover after 5 sessions: +3.8% net, 11 of 12 (t 3.4); 15 sessions +4.9%, 83%; 21 sessions +3.7%, 75%. Random same-stock shorts −2.4%. 10 of 12 events negative vs WIG20 over the next month (JSW −28, MBK −14, ZAB −14, BDX −11, PCO −7, CDR −7, ALR −6, MIL −3; DNP +6, BDX 2023 +2). The "run-up" from announcement to effective date does not exist (−1.1 pp) — the inclusion is priced on the announcement day (+2.7%) and the passive buying at the effective close is what gets reversed. **Caveat that decides tradability:** most of the drop is on the first session after the flow day (entry one session later gives only +0.9%, 58%). The short has to be opened at or into the effective-day close; XTB CFDs stop trading before the closing auction, so the fill is the ~16:50 price, not the fixing — intraday data for the 12 effective days are needed to confirm how much of the spike is in the auction itself. Also: 12 events in 10 years, ~1–2 a year. Next review: announced ~5 Nov 2026, effective 24 Nov 2026 close (analysts expect no Polish changes).

Also real but unusable for her: Small Cap additions fall 5.8 pp between announcement and effective date (short +1.6% net, n=19) — the names are not shortable on XTB.
