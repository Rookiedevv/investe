# Round 12c: domestic sector read-through outside banks. First reporter of the quarter in a sector -> trade the later reporters until their own report.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
from cal_timing import events
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
def cst(t): return 1.0 if t in L1 else (1.5 if t in L2 else 2.5)
SECT={'developers':['DOM','1AT','DVL','ATT'],'construction':['BDX','MRB','TOR','UNI','ERB'],'utilities':['PGE','TPE','ENA'],
      'retail':['LPP','CCC','VRG','PCO','ALE','DNP','EUR','ZAB'],'gaming':['CDR','11B','TEN','PLW','HUG'],'it':['ACP','CLN','TXT','ATT'],
      'telecom-media':['OPL','CPS','WPL'],'finance-other':['KRU','GPW','XTB','PZU'],'industrial':['KTY','STP','KGH','JSW','LWB','GEA','APR','CAR']}
E=events(); E=E[(E.date>='2016-01-01')&(E.timing.isin(['b','a','d']))]
# reaction day per filing; first-news filter per ticker (30 sessions)
rows=[]
for t,g in E.groupby('t'):
    if t not in AD: continue
    ii=[idx.searchsorted(d) for d in g.date]
    for (_,e),i in zip(g.iterrows(),ii):
        if i>=len(idx) or idx[i]!=e.date or any(0<i-j<=30 for j in ii): continue
        k=i+1 if e.timing=='a' else i
        if k<1 or k>=len(idx): continue
        a=AD[t]
        if not(np.isfinite(a.iloc[k-1]) and np.isfinite(a.iloc[k])): continue
        rows.append(dict(t=t,k=k,d=idx[k],re=(a.iloc[k]/a.iloc[k-1]-1)*100-(W.iloc[k]/W.iloc[k-1]-1)*100))
F=pd.DataFrame(rows)
out=[]
for sec,names in SECT.items():
    f=F[F.t.isin(names)].sort_values('k')
    # cluster into quarters: a new cluster starts when gap to previous filing in the sector > 25 sessions
    cl=[];c=-1;last=-999
    for k in f.k:
        if k-last>25: c+=1
        cl.append(c); last=k
    f=f.assign(c=cl)
    for c,g in f.groupby('c'):
        g=g.sort_values('k'); first=g.iloc[0]
        for _,x in g.iloc[1:].iterrows():
            if x.k-first.k<2 or x.k-first.k>45 or x.t==first.t: continue
            i0=first.k; i1=x.k            # long later reporter from first's reaction close to its own reaction close
            r=(AD[x.t].iloc[i1]/AD[x.t].iloc[i0]-1)*100-cst(x.t)
            out.append(dict(sec=sec,d=idx[i0],first=first.t,re1=first.re,t=x.t,n=i1-i0,r=r,x=r-bench(i0,i1),re2=x.re))
D=pd.DataFrame(out); print('pairs:',len(D))
def rep(g,lab):
    if len(g)<5: print(f"{lab:48s} n={len(g)}"); return
    y=g.d.dt.year; tt=g.x.mean()/g.x.std()*np.sqrt(len(g))
    print(f"{lab:48s} n={len(g):3d} net {g.r.mean():+5.2f}% | vs ETF {g.x.mean():+5.2f}pp med {g.x.median():+5.2f} t {tt:4.1f} beats {100*(g.x>0).mean():3.0f}% | <2022 {g.x[y<2022].mean():+5.2f} 2022+ {g.x[y>=2022].mean():+5.2f} | corr(re1,re2) {g.re1.corr(g.re2):+.2f} corr(re1,x) {g.re1.corr(g.x):+.2f}")
for sec,g in D.groupby('sec'):
    print('\n==',sec)
    rep(g,'all pairs'); rep(g[g.re1>=3],'first reporter >= +3%'); rep(g[g.re1<=-3],'first reporter <= -3%'); rep(g[g.re1.abs()<3],'first reporter within +-3%')
print('\n== all sectors pooled')
rep(D,'all'); rep(D[D.re1>=3],'first >= +3%'); rep(D[D.re1<=-3],'first <= -3%')
g=D[D.re1<=-3].copy(); g['sh']=-(g.r+g.t.map(cst))-(0.6+0.3+0.7*g.n/252)
print('first <= -3pct: XTB short of later reporters, abs net %.2f%% win %.0f%% n=%d'%(g.sh.mean(),100*(g.sh>0).mean(),len(g)))
print('\n== liquid later reporters only (L1+L2)')
L=D[D.t.isin(L1|L2)]; rep(L,'all'); rep(L[L.re1>=3],'first >= +3%'); rep(L[L.re1<=-3],'first <= -3%')
