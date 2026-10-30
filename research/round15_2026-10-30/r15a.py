# Round 15a: Polish 10-year yield (FRED IRLTLT01PLM156N, monthly average) vs banks / utilities / WIG20 next month. Monthly: signal = change in the yield
# over the past 1 / 3 months (known at month end, since the monthly average is only known after the month closes -> we lag one extra month to be safe).
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
y=pd.read_csv(os.path.join(H,'pl10y.csv'),parse_dates=['date']).set_index('date')['value']
banks=[t for t in ['PKO','PEO','MBK','ALR','ING','MIL','EBP','BNP','BHW'] if t in AD]; utils=[t for t in ['PGE','TPE','ENA'] if t in AD]
M=AD.resample('ME').last(); Wm=W.resample('ME').last(); Em=ETF.resample('ME').last()
def basket(names): return (M[names].pct_change()).mean(axis=1)*100   # equal-weight monthly return, rebalanced
rb=basket(banks); ru=basket(utils); rw=Wm.pct_change()*100; re_=Em.pct_change()*100
ym=y.copy(); ym.index=ym.index+pd.offsets.MonthEnd(0)
d1=ym.diff(1); d3=ym.diff(3)
df=pd.DataFrame({'d1':d1,'d3':d3,'lvl':ym}).reindex(rb.index)
# signal known at end of month m uses the yield average of month m (published ~first days of m+1) -> trade month m+2; conservative: shift by 2
for lag in (1,2):
    print(f'\n== lag {lag} month(s) between the yield move and the traded month')
    sig=df.shift(lag)
    for name,r in (('banks (EW)',rb),('utilities (EW)',ru),('WIG20',rw)):
        x=pd.concat([sig,r.rename('r'),(r-re_).rename('x')],axis=1).dropna(); x=x[x.index>='2012-01-01']
        print(f"{name:16s} corr(d1,r) {x.d1.corr(x.r):+.2f} corr(d3,r) {x.d3.corr(x.r):+.2f} | months with 3m yield up > 0.5pp: n={int((x.d3>0.5).sum())} r {x.r[x.d3>0.5].mean():+.2f} vsETF {x.x[x.d3>0.5].mean():+.2f} | down < -0.5pp: n={int((x.d3<-0.5).sum())} r {x.r[x.d3<-0.5].mean():+.2f} vsETF {x.x[x.d3<-0.5].mean():+.2f} | all r {x.r.mean():+.2f}")
    x=pd.concat([sig,rb.rename('r'),(rb-re_).rename('x')],axis=1).dropna(); x=x[x.index>='2012-01-01']
    for lo,hi in ((-9,-0.5),(-0.5,0),(0,0.5),(0.5,9)):
        s=x[(x.d3>=lo)&(x.d3<hi)]; print(f"   banks, 3m yield change {lo}..{hi}: n={len(s)} r {s.r.mean():+.2f} vsETF {s.x.mean():+.2f} win {100*(s.x>0).mean():.0f}%")
