# Round 12d: design variants of the live pre-session results-drift rule (L1, reaction +3..6% vs WIG20): entry lag, holding period, prior momentum, volume.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
from cal_timing import events
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
E=events(); E=E[(E.date>='2016-01-01')&(E.timing=='b')]
sig=[]
for t,g in E.groupby('t'):
    if t not in AD or t not in L1 or t=='XTB': continue
    ii=[idx.searchsorted(d) for d in g.date]
    for (_,e),i in zip(g.iterrows(),ii):
        if i>=len(idx) or idx[i]!=e.date or any(0<i-j<=30 for j in ii) or i<130 or i+70>=len(idx): continue
        a=AD[t]
        if not(np.isfinite(a.iloc[i-1]) and np.isfinite(a.iloc[i])): continue
        re=(a.iloc[i]/a.iloc[i-1]-1)*100-(W.iloc[i]/W.iloc[i-1]-1)*100
        if 3<=re<6: sig.append((t,i,re))
print('signals (L1 ex XTB, +3..6%, pre-session, first news):',len(sig))
def run(lag,hold,label,filt=None):
    rows=[]
    for t,i,re in sig:
        i0=i+lag; i1=i0+hold; a=AD[t]
        if filt and not filt(t,i): continue
        if not(np.isfinite(a.iloc[i0]) and np.isfinite(a.iloc[i1])): continue
        r=(a.iloc[i1]/a.iloc[i0]-1)*100-1.0; rows.append(dict(t=t,d=idx[i0],r=r,x=r-bench(i0,i1)))
    g=pd.DataFrame(rows)
    if len(g)<5: print(f"{label:44s} n={len(g)}"); return
    y=g.d.dt.year; tt=g.x.mean()/g.x.std()*np.sqrt(len(g))
    print(f"{label:44s} n={len(g):3d} net {g.r.mean():+5.2f}% | vs ETF {g.x.mean():+5.2f}pp med {g.x.median():+5.2f} t {tt:4.1f} beats {100*(g.x>0).mean():3.0f}% | <2022 {g.x[y<2022].mean():+5.2f} 2022+ {g.x[y>=2022].mean():+5.2f} | per-day {g.x.mean()/hold:+.3f}")
print('\n== entry lag (hold 21 from entry)')
for lag in (0,1,2,3,5): run(lag,21,f"enter {lag} sessions after the reaction day")
print('\n== holding period (entry at reaction close)')
for hold in (5,10,15,21,30,42,63): run(0,hold,f"hold {hold} sessions")
print('\n== exit on reaction day + N but enter at lag 1 (missed-signal case)')
for hold in (10,20): run(1,hold,f"lag 1, hold {hold}")
print('\n== prior momentum filters (entry at reaction close, hold 21)')
def mom(t,i,n): return (AD[t].iloc[i-1]/AD[t].iloc[i-1-n]-1)*100-(W.iloc[i-1]/W.iloc[i-1-n]-1)*100
run(0,21,'prior 126d vs WIG20 > 0',lambda t,i: mom(t,i,126)>0); run(0,21,'prior 126d vs WIG20 <= 0',lambda t,i: mom(t,i,126)<=0)
run(0,21,'prior 21d vs WIG20 > 0',lambda t,i: mom(t,i,21)>0); run(0,21,'prior 21d vs WIG20 <= 0',lambda t,i: mom(t,i,21)<=0)
def dist_hi(t,i): a=AD[t].iloc[i-250:i]; return (AD[t].iloc[i]/a.max()-1)*100
run(0,21,'close within 5% of 52w high',lambda t,i: dist_hi(t,i)>-5); run(0,21,'close more than 5% below 52w high',lambda t,i: dist_hi(t,i)<=-5)
run(0,21,'close more than 20% below 52w high',lambda t,i: dist_hi(t,i)<=-20)
print('\n== market regime at signal')
run(0,21,'WIG20 above its 200d average',lambda t,i: W.iloc[i]>W.iloc[i-200:i].mean()); run(0,21,'WIG20 below its 200d average',lambda t,i: W.iloc[i]<=W.iloc[i-200:i].mean())
print('\n== reaction-day range: close near the day high (strong close) vs not')
def strong(t,i):
    p=P[t].reindex(idx); h,l,c=p['high'].iloc[i],p['low'].iloc[i],p['close'].iloc[i]
    return np.nan if not np.isfinite(h) or h==l else (c-l)/(h-l)
run(0,21,'close in top third of day range',lambda t,i: strong(t,i)>=0.67); run(0,21,'close in lower two thirds',lambda t,i: strong(t,i)<0.67)
