# Round 19a: (1) pre-session drift signals x KNF aggregate short interest (short-squeeze fuel?) x analyst reaction (target raises within 5 sessions);
# (2) short-horizon WIG20 patterns re-costed for the XTB W20 CFD (spread ~1.8 pts ~0.05% + 0.03%/day financing) instead of the ETF's 0.78%.
import os,sys; H=os.path.dirname(os.path.abspath(__file__))
for p in ('round12_2026-10-30','round9_2026-10-30'): sys.path.insert(0,os.path.join(H,'..',p))
from lib import *
from cal_timing import events
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
BANKS=set('PKO PEO MBK ALR ING MIL EBP BNP BHW'.split())
A=pd.read_csv(os.path.join(H,'..','round17_2026-10-30','knf','aggregate_short_interest.csv'),index_col=0,parse_dates=True).reindex(idx).ffill().fillna(0)
recs=pd.read_csv(os.path.join(H,'..','round9_2026-10-30','recs.csv'),parse_dates=['issue_date']).dropna(subset=['issue_date'])
recs['up']=recs.target>recs.prev_target; recs['dn']=recs.target<recs.prev_target
E=events(); E=E[(E.date>='2014-01-01')&(E.timing=='b')].sort_values(['t','date'])
rows=[]
for t,g in E.groupby('t'):
    if t not in AD or t=='XTB' or t in BANKS: continue
    a=AD[t]; ii=[idx.searchsorted(d) for d in g.date]
    for (_,e),i in zip(g.iterrows(),ii):
        if i>=len(idx) or idx[i]!=e.date or any(0<i-j<=30 for j in ii) or i<30 or i+22>=len(idx): continue
        if not(np.isfinite(a.iloc[i-1]) and np.isfinite(a.iloc[i]) and np.isfinite(a.iloc[i+21])): continue
        re=(a.iloc[i]/a.iloc[i-1]-1)*100-(W.iloc[i]/W.iloc[i-1]-1)*100
        c=1.0 if t in L1 else (1.5 if t in L2 else 2.5)
        r=(a.iloc[i+21]/a.iloc[i]-1)*100-c
        si=A[t].iloc[i] if t in A else 0.0
        rr=recs[(recs.ticker==t)&(recs.issue_date>idx[i])&(recs.issue_date<=idx[i+5])]
        rows.append(dict(t=t,d=idx[i],re=re,r=r,x=r-bench(i,i+21),si=si,si_chg=si-(A[t].iloc[i-21] if t in A else 0),nup=rr.up.sum(),ndn=rr.dn.sum(),nrec=len(rr),liq=t in LIQ))
D=pd.DataFrame(rows); D['y']=D.d.dt.year
def rep(g,lab):
    if len(g)<5: print(f"{lab:54s} n={len(g)}"); return
    print(f"{lab:54s} n={len(g):3d} net {g.r.mean():+5.2f} vsETF {g.x.mean():+5.2f} med {g.x.median():+5.2f} beats {100*(g.x>0).mean():3.0f}% t {g.x.mean()/g.x.std()*np.sqrt(len(g)):4.1f} | <2022 {g.x[g.y<2022].mean():+5.2f} 2022+ {g.x[g.y>=2022].mean():+5.2f}")
S=D[(D.re>=3)&(D.re<6)&D.liq]; print('pre-session, first news, +3..6%, liquid ex banks ex XTB:')
rep(S,'all'); rep(S[S.si>0],'  with an open KNF short position (>=0.5%)'); rep(S[S.si==0],'  no disclosed short'); rep(S[S.si>=1],'  aggregate short >= 1%'); rep(S[S.si_chg>0],'  short interest rose over prior month')
rep(S[S.nup>0],'  >=1 target raise within 5 sessions'); rep(S[(S.nrec>0)&(S.nup==0)],'  recs within 5 sessions but no raise'); rep(S[S.nrec==0],'  no recommendation within 5 sessions')
S2=D[(D.re>=2)&D.liq]; print('\nwider: +2% and above, liquid ex banks ex XTB:')
rep(S2,'all'); rep(S2[S2.si>=1],'  aggregate short >= 1%'); rep(S2[S2.si==0],'  no disclosed short'); rep(S2[S2.nup>=2],'  >=2 target raises within 5 sessions'); rep(S2[S2.nup==0],'  no target raise')
N=D[(D.re<=-3)&D.liq]; print('\nnegative pre-session reactions <= -3% (long = contrarian):')
rep(N,'all'); rep(N[N.si>=1],'  aggregate short >= 1% (crowded short, bounce?)'); rep(N[N.si==0],'  no disclosed short'); rep(N[N.ndn>0],'  >=1 target cut within 5 sessions'); rep(N[N.ndn==0],'  no target cut')
# ---- (2) WIG20 short-horizon patterns with W20 CFD costs
print('\n== WIG20 short-horizon patterns, XTB W20 CFD cost 0.05% + 0.03%/day (long side) ==')
w=W.dropna(); r=w.pct_change()*100
def test(cond,lab):
    out=f"{lab:38s}"
    for hold in (1,2,3,5,10):
        rows=[];last=-99
        for i in range(260,len(w)-hold-1):
            if not cond(i) or i-last<hold: continue
            last=i; rows.append(((w.iloc[i+hold]/w.iloc[i]-1)*100-0.05-0.03*hold, w.index[i].year))
        x=np.array([a for a,_ in rows]); y=np.array([b for _,b in rows]); base=((w.shift(-hold)/w-1)*100).mean()-0.05-0.03*hold
        out+=f" | h{hold:2d} n={len(x):3d} {x.mean():+5.2f} (unc {base:+5.2f}) win {100*(x>0).mean():3.0f}% 2019+ {x[y>=2019].mean():+5.2f}"
    print(out)
test(lambda i: r.iloc[i]<=-3,'day <= -3%'); test(lambda i: r.iloc[i]<=-2,'day <= -2%'); test(lambda i: (w.iloc[i]/w.iloc[i-2]-1)*100<=-4,'2 days <= -4%')
test(lambda i: (w.iloc[i]/w.iloc[i-5]-1)*100<=-5,'5 days <= -5%'); test(lambda i: r.iloc[i]<=-2 and r.iloc[i-1]<=-1,'two down days (-2 then -1)')
test(lambda i: r.iloc[i]>=2,'day >= +2%'); test(lambda i: w.iloc[i]<w.iloc[i-20:i].min(),'new 20-day low'); test(lambda i: w.iloc[i]>w.iloc[i-20:i].max(),'new 20-day high')
# RSI(2)-style: two consecutive closes down and close < 5-day low
test(lambda i: r.iloc[i]<0 and r.iloc[i-1]<0 and w.iloc[i]<w.iloc[i-5:i].min(),'2 down days + 5-day low')
