# Round 20a: size rotation among the three GPW size indices, all of which have Beta ETFs in eMakler (ETFBW20TR, ETFBM40TR, ETFBS80TR).
# Data: indices_monthly.csv (bankier, month-end closes; price indices MWIG40/SWIG80 from 1997/1994, WIG20 from data/prices) and the TR indices daily from 2017-09.
# Monthly decision at month end, hold one month, 0.78% round trip charged only when the holding changes. Benchmark = buy & hold WIG20 (same index family).
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
M=pd.read_csv(os.path.join(H,'indices_monthly.csv'),parse_dates=['date'])
def monthly(sym):
    s=M[M.symbol==sym].set_index('date').close; s.index=s.index.to_period('M'); return s[~s.index.duplicated(keep='last')]
w20=pd.read_csv(R+'/data/prices/WIG20.csv',parse_dates=['date']).set_index('date').close.dropna(); w20m=w20.groupby(w20.index.to_period('M')).last()
PX=pd.DataFrame({'WIG20':w20m,'MWIG40':monthly('MWIG40'),'SWIG80':monthly('SWIG80')}).dropna()
PX=PX[(PX.index>='2004-12')&(PX.index<='2025-12')]
# add the TR cushion so WIG20 is not penalised for its higher dividends: approx yields WIG20 3.5%, mWIG40 2.0%, sWIG80 2.0%/yr
Y={'WIG20':0.035,'MWIG40':0.02,'SWIG80':0.02}
R=PX.pct_change(); 
for c in R: R[c]=R[c]+Y[c]/12
def run(score,lab,cost=0.0078,top=1,cash_rule=None):
    hold=None; rets=[]; sw=0
    for i in range(14,len(R)):
        sc=score(PX.iloc[:i])  # uses data up to month-end i-1 (decision at that close)
        if sc is None: continue
        pick=list(sc.sort_values(ascending=False).index[:top])
        if cash_rule is not None and cash_rule(PX.iloc[:i],pick): pick=[]
        r=np.mean([R.iloc[i][p] for p in pick]) if pick else 0.004  # cash ~4.8%/yr deposit proxy
        if set(pick)!=set(hold or []): r-=cost; sw+=1
        hold=pick; rets.append((R.index[i],r,R.iloc[i]['WIG20']))
    d=pd.DataFrame(rets,columns=['m','r','b']).set_index('m'); x=(d.r-d.b)*100
    cum=lambda s:(1+s).prod()**(12/len(s))-1
    print(f"{lab:44s} months={len(d):3d} switches={sw:3d} | ann {100*cum(d.r):+5.1f}% vs WIG20 {100*cum(d.b):+5.1f}% | excess {x.mean():+5.2f} pp/month, beats {100*(x>0).mean():3.0f}% of months, t {x.mean()/x.std()*np.sqrt(len(x)):4.1f} | 2005-14 {x[x.index<'2015'].mean():+5.2f} 2015-25 {x[x.index>='2015'].mean():+5.2f}")
    return d
mom=lambda n:(lambda P:(P.iloc[-1]/P.iloc[-1-n]-1))
print('== pick the size index with the best past-n-month return (monthly, 2006-2025, price indices + dividend cushion) ==')
for n in (1,3,6,12): run(mom(n),f'best past {n}m')
run(lambda P:(P.iloc[-2]/P.iloc[-13]-1),'best 12-1 momentum')
run(lambda P:(P.iloc[-1]/P.iloc[-13]-1)*-1,'WORST past 12m (reversal)')
run(lambda P:(P.iloc[-1]/P.iloc[-2]-1)*-1,'WORST past 1m (reversal)')
print('\n== two-way: small vs large only (sWIG80 if it beat WIG20 over n months, else WIG20) ==')
for n in (3,6,12):
    run(lambda P,n=n: pd.Series({'WIG20':0.0,'SWIG80':(P.SWIG80.iloc[-1]/P.SWIG80.iloc[-1-n])-(P.WIG20.iloc[-1]/P.WIG20.iloc[-1-n])}),f'sWIG80 vs WIG20, {n}m relative')
print('\n== absolute-momentum overlay: cash when the picked index is below its 12-month-ago level ==')
run(mom(6),'best 6m + cash if 12m<0',cash_rule=lambda P,pick: pick and P[pick[0]].iloc[-1]<P[pick[0]].iloc[-13])
run(mom(12),'best 12m + cash if 12m<0',cash_rule=lambda P,pick: pick and P[pick[0]].iloc[-1]<P[pick[0]].iloc[-13])
run(lambda P:pd.Series({'WIG20':0.0}),'WIG20 + cash if WIG20 12m<0',cash_rule=lambda P,pick: P.WIG20.iloc[-1]<P.WIG20.iloc[-13])
run(lambda P:pd.Series({'WIG20':0.0}),'WIG20 + cash if below 10-month average',cash_rule=lambda P,pick: P.WIG20.iloc[-1]<P.WIG20.iloc[-10:].mean())
print('\n== buy & hold each (ann, 2006-2025) ==')
for c in R: print(f"  {c}: {100*((1+R[c].iloc[14:]).prod()**(12/(len(R)-14))-1):+.1f}%/yr (with dividend cushion)")
# TR check 2018-2025 on the real TR indices
D=pd.read_csv(os.path.join(H,'indices_daily.csv'),parse_dates=['date'])
T=D.pivot(index='date',columns='symbol',values='close').dropna(); Tm=T.groupby(T.index.to_period('M')).last()
PX=Tm.rename(columns={'WIG20TR':'WIG20','MWIG40TR':'MWIG40','SWIG80TR':'SWIG80'}); R=PX.pct_change()
print('\n== same on the real TR indices, 2018-10 .. 2025-12 ==')
for n in (1,3,6,12): run(mom(n),f'TR: best past {n}m')
run(lambda P:pd.Series({'WIG20':0.0,'SWIG80':(P.SWIG80.iloc[-1]/P.SWIG80.iloc[-7])-(P.WIG20.iloc[-1]/P.WIG20.iloc[-7])}),'TR: sWIG80 vs WIG20, 6m relative')
