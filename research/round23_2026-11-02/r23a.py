# Round 23a: Poland sovereign rating actions (Fitch / Moody's / S&P) -> next-session and 1-month moves.
import pandas as pd, numpy as np, pathlib
R = '/home/claude/investe'
def ld(t):
    d = pd.read_csv(f'{R}/data/prices/{t}.csv', parse_dates=['date']).set_index('date').sort_index()
    return d[~d.index.duplicated()]
W = ld('WIG20'); F = ld('FW20'); E = ld('EURPLN'); ETF = ld('ETFBW20TR')
for s in pathlib.Path(f'{R}/data/prices/seed').glob('*.csv'):
    d = pd.read_csv(s, parse_dates=['Data']).rename(columns={'Data':'date','Otwarcie':'open','Zamkniecie':'close'}).set_index('date').sort_index()
    if s.stem.upper().startswith('WIG20') and len(d) > len(W): W = d[~d.index.duplicated()]
    if s.stem.upper().startswith('FW20') and len(d) > len(F): F = d[~d.index.duplicated()]
BANKS = ['PKO', 'PEO', 'MBK', 'ALR', 'ING', 'MIL', 'BHW', 'EBP', 'BNP']
B = pd.DataFrame({b: ld(b)['adj_close'] for b in BANKS}).pct_change().mean(axis=1)   # equal-weight daily return
idx = W.index
# (announcement date, agency, action, sign) ; announcements are Friday/weekday evenings after the Warsaw close
EV = """2007-01-18 Fitch upgrade BBB+->A- +1|2007-03-29 S&P upgrade BBB+->A- +1|2008-02-21 S&P outlook stable->positive +1|2008-10-27 S&P outlook positive->stable -1|
2013-02-21 Fitch outlook stable->positive +1|2013-08-23 Fitch outlook positive->stable -1|2015-02-06 S&P outlook stable->positive +1|2016-01-15 S&P downgrade A-->BBB+ neg -1|
2016-05-13 Moody's outlook stable->negative -1|2016-12-02 S&P outlook negative->stable +1|2017-05-12 Moody's outlook negative->stable +1|2018-04-13 S&P outlook stable->positive +1|
2018-10-12 S&P upgrade BBB+->A- +1|2025-09-05 Fitch outlook stable->negative -1|2025-09-19 Moody's outlook stable->negative -1|2026-09-18 Moody's downgrade A2->A3 stable -1"""
rows = []
for x in EV.replace('\n', '').split('|'):
    p = x.split(); d = pd.Timestamp(p[0]); sg = int(p[-1]); lab = ' '.join(p[1:-1])
    i = idx.searchsorted(d, side='right')            # first session AFTER the announcement day
    if i + 21 >= len(idx): continue
    i0 = i - 1                                        # close of the announcement day
    def r(s, a, b): return (s.iloc[b] / s.iloc[a] - 1) * 100
    gapF = (F.open.reindex(idx).iloc[i] / F.close.reindex(idx).iloc[i0] - 1) * 100
    occF = (F.close.reindex(idx).iloc[i] / F.open.reindex(idx).iloc[i] - 1) * 100
    w1 = r(W.close, i0, i); w21 = r(W.close, i, i + 21); pre5 = r(W.close, i0 - 5, i0)
    b1 = B.reindex(idx).iloc[i] * 100
    b21 = ((1 + B.reindex(idx).iloc[i + 1:i + 22]).prod() - 1) * 100
    e1 = (E.close.reindex(idx).ffill().iloc[i] / E.close.reindex(idx).ffill().iloc[i0] - 1) * 100
    rows.append(dict(date=d.date(), lab=lab, sg=sg, pre5=pre5, FW20_gap=gapF, FW20_o2c=occF, WIG20_d1=w1, banks_d1=b1, EURPLN_d1=e1, WIG20_21=w21, banks_21=b21))
df = pd.DataFrame(rows)
# unconditional baseline: all sessions since 2007 (FW20 gap and open->close; WIG20 1d and 21d)
fo, fc = F.open.reindex(idx), F.close.reindex(idx)
base = dict(gap=((fo / fc.shift(1) - 1) * 100)['2007':].abs().mean(), o2c=((fc / fo - 1) * 100)['2007':].mean(),
            w21=((W.close.shift(-21) / W.close - 1) * 100)['2007':].mean(), sdw1=(W.close.pct_change() * 100)['2007':].std())
pd.set_option('display.width', 220)
print(df.round(2).to_string(index=False))
print('\nbaseline: mean |FW20 gap| %.2f%%, FW20 open->close %.3f%%, WIG20 21d %+.2f%%, WIG20 daily SD %.2f%%' % (base['gap'], base['o2c'], base['w21'], base['sdw1']))
for sg, name in ((-1, 'negative actions'), (1, 'positive actions')):
    g = df[df.sg == sg]
    print(f"{name:17s} n={len(g)} | pre5 {g.pre5.mean():+.2f} | FW20 gap {g.FW20_gap.mean():+.2f} (neg {100*(g.FW20_gap<0).mean():.0f}%) | FW20 open->close {g.FW20_o2c.mean():+.2f} "
          f"| WIG20 d1 {g.WIG20_d1.mean():+.2f} | banks d1 {g.banks_d1.mean():+.2f} | EURPLN d1 {g.EURPLN_d1.mean():+.2f} | WIG20 +21 {g.WIG20_21.mean():+.2f} | banks +21 {g.banks_21.mean():+.2f}")
df.to_csv('r23a_events.csv', index=False)
