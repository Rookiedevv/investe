# Round 18b: cross-sectional monthly reversal / continuation among liquid names (L1+L2): at each month end rank the past 21-session return
# vs WIG20; buy the bottom 5 (reversal) or top 5 (continuation) at the close, hold 21 sessions, eMakler costs, vs the ETF.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
def cst(t): return 1.0 if t in L1 else 1.5
U=[t for t in AD.columns if t in LIQ]
A=AD[U]
def relret(n): return (A/A.shift(n)-1).sub(W/W.shift(n)-1,axis=0)*100
REL={n:relret(n) for n in (5,21,63)}
me=[i for i in range(260,len(idx)-22) if idx[i].month!=idx[i+1].month]
def run(pick,lab,k=5,lookback=21,hold=21):
    rows=[]
    for i in me:
        r=REL[lookback].iloc[i].dropna()
        if len(r)<15: continue
        sel=pick(r,k)
        for t in sel:
            p0,p1=A[t].iloc[i],A[t].iloc[i+hold]
            if not(np.isfinite(p0) and np.isfinite(p1)): continue
            rr=(p1/p0-1)*100-cst(t); rows.append(dict(d=idx[i],t=t,r=rr,x=rr-bench(i,i+hold)))
    g=pd.DataFrame(rows); m=g.groupby('d').x.mean(); y=m.index.year
    print(f"{lab:46s} months={len(m):3d} net {g.r.mean():+5.2f} vsETF {m.mean():+5.2f} pp/month, beats ETF {100*(m>0).mean():3.0f}% of months, t {m.mean()/m.std()*np.sqrt(len(m)):4.1f} | <2019 {m[y<2019].mean():+5.2f} 2019+ {m[y>=2019].mean():+5.2f}")
    return g
run(lambda r,k: r.nsmallest(k).index,'bottom 5 past-month laggards (reversal)')
run(lambda r,k: r.nlargest(k).index,'top 5 past-month leaders (continuation)')
run(lambda r,k: r.nsmallest(k).index,'bottom 5 by past 5 sessions',lookback=5)
run(lambda r,k: r.nsmallest(k).index,'bottom 5 by past 63 sessions',lookback=63)
run(lambda r,k: r[r<=-10].index,'all names >= 10 pp behind WIG20 in a month')
run(lambda r,k: r[r<=-15].index,'all names >= 15 pp behind')
run(lambda r,k: r[r>=10].index,'all names >= 10 pp ahead')
run(lambda r,k: r.nsmallest(3).index,'bottom 3')
