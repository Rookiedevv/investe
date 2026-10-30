# Round 18c: does the pre-session results drift depend on the company's recent report history? "Serial drifters": condition the live rule
# (L1 ex banks ex XTB, first news of the quarter, pre-session filing, reaction +3..6% vs WIG20, buy at close, hold 21) on
# (a) the previous report's reaction sign, (b) whether the previous report's 21-day post-drift was positive, (c) the number of positive reactions in the last 4 reports.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round12_2026-10-30')); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
from cal_timing import events
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
BANKS=set('PKO PEO MBK ALR ING MIL EBP BNP BHW'.split())
E=events(); E=E[(E.date>='2014-01-01')].sort_values(['t','date'])
rows=[]
for t,g in E.groupby('t'):
    if t not in AD or t=='XTB': continue
    a=AD[t]; hist=[]  # (reaction, drift21) of every first-news report, any timing
    ii=[idx.searchsorted(d) for d in g.date]
    for (_,e),i in zip(g.iterrows(),ii):
        if i>=len(idx) or idx[i]!=e.date or any(0<i-j<=30 for j in ii) or i<30 or i+22>=len(idx): continue
        if not(np.isfinite(a.iloc[i-1]) and np.isfinite(a.iloc[i]) and np.isfinite(a.iloc[i+21])): continue
        re=(a.iloc[i]/a.iloc[i-1]-1)*100-(W.iloc[i]/W.iloc[i-1]-1)*100
        dr=(a.iloc[i+21]/a.iloc[i]-1)*100-(W.iloc[i+21]/W.iloc[i]-1)*100
        prev=hist[-1] if hist else None; last4=hist[-4:]
        if e.timing=='b' and 3<=re<6 and t in L1 and t not in BANKS:
            r=(a.iloc[i+21]/a.iloc[i]-1)*100-1.0
            rows.append(dict(t=t,d=idx[i],re=re,r=r,x=r-bench(i,i+21),prev_re=prev[0] if prev else np.nan,prev_dr=prev[1] if prev else np.nan,
                             npos4=sum(1 for h in last4 if h[0]>0) if len(last4)==4 else np.nan,ndrift4=sum(1 for h in last4 if h[1]>0) if len(last4)==4 else np.nan))
        hist.append((re,dr))
D=pd.DataFrame(rows); print('live-rule signals 2014-26 (L1 ex banks ex XTB):',len(D))
def rep(g,lab):
    if len(g)<5: print(f"{lab:48s} n={len(g)}"); return
    y=g.d.dt.year; print(f"{lab:48s} n={len(g):3d} net {g.r.mean():+5.2f} vsETF {g.x.mean():+5.2f} med {g.x.median():+5.2f} beats {100*(g.x>0).mean():3.0f}% t {g.x.mean()/g.x.std()*np.sqrt(len(g)):4.1f} | <2022 {g.x[y<2022].mean():+5.2f} 2022+ {g.x[y>=2022].mean():+5.2f}")
rep(D,'all'); rep(D[D.prev_re>0],'previous report reaction > 0'); rep(D[D.prev_re<=0],'previous report reaction <= 0')
rep(D[D.prev_re>=3],'previous reaction >= +3% too (back-to-back beats)'); rep(D[D.prev_dr>0],'previous report drifted up after'); rep(D[D.prev_dr<=0],'previous report drifted down after')
rep(D[D.npos4>=3],'>=3 of last 4 reactions positive'); rep(D[D.npos4<=1],'<=1 of last 4 positive'); rep(D[D.ndrift4>=3],'>=3 of last 4 post-report drifts positive'); rep(D[D.ndrift4<=1],'<=1 of last 4 drifts positive')
print('\nper ticker:'); 
for t,g in D.groupby('t'):
    if len(g)>=4: print(f"  {t:4s} n={len(g):2d} vsETF {g.x.mean():+5.2f} beats {100*(g.x>0).mean():3.0f}%")
D.to_csv(os.path.join(H,'r18c_signals.csv'),index=False)
