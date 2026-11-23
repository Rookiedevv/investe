from fac36 import *
from sectors import SEC
print('unmapped:', [t for t in TICK if t not in SEC])
for lab, a, b in (('LARGE >=30m', 30e6, None), ('MID 10-30m', 10e6, 30e6), ('SMALL-LIQ 2-10m', 2e6, 10e6), ('>=10m', 10e6, None)):
    print('==', lab)
    for k in ('mom12_1', 'mom6', 'rev1 (1m losers)', 'near 52w high', 'lowvol250', 'range pos 21d', 'mom12_1/vol'):
        evaluate(FACT[k], k, mint=a, maxt=b, minn=8, q=0.34, k=3)
