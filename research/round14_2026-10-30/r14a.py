# Round 14a: quarterly revenue acceleration (the Asbis / car-parts logic on quarterly reports). Revenue from biznesradar quarterly income statements
# (revenue/<T>.csv, thousands PLN). Signal known at the first-news filing for that quarter (cal_timing events): acc = y/y growth of the quarter
# minus the mean y/y of the previous three quarters. Entry at the reaction-day close (filing day if pre-session, next day if after), hold 21 / 63.
import os,sys,glob; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30')); sys.path.insert(0,os.path.join(H,'..','round12_2026-10-30'))
from lib import *
from cal_timing import events
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
def cst(t): return 1.0 if t in L1 else (1.5 if t in L2 else 2.5)
E=events()
rows=[]
for f in sorted(glob.glob(os.path.join(H,'revenue','*.csv'))):
    t=os.path.basename(f)[:-4]
    if t not in AD: continue
    q=pd.read_csv(f); q['y']=q.quarter.str[:4].astype(int); q['n']=q.quarter.str[-1].astype(int)
    q=q.sort_values(['y','n']).reset_index(drop=True); q['yoy']=q.revenue.pct_change(4)*100
    q['acc']=q.yoy-q.yoy.shift(1).rolling(3).mean()
    ev=E[(E.t==t)&(E.timing.isin(['b','a','d']))].sort_values('date')
    for _,x in q.dropna(subset=['acc']).iterrows():
        qend=pd.Timestamp(year=x.y+(1 if x.n==4 else 0),month={1:3,2:6,3:9,4:12}[x.n],day=1)+pd.offsets.MonthEnd(0)
        cand=ev[(ev.date>qend+pd.Timedelta(days=7))&(ev.date<=qend+pd.Timedelta(days=150))]
        if cand.empty: continue
        e=cand.iloc[0]; i=idx.searchsorted(e.date)
        if i>=len(idx) or idx[i]!=e.date: continue
        k=i+1 if e.timing=='a' else i
        if k<1 or k+63>=len(idx): continue
        a=AD[t]
        if not all(np.isfinite(a.iloc[j]) for j in (k-1,k,k+21,k+63)): continue
        re=(a.iloc[k]/a.iloc[k-1]-1)*100-(W.iloc[k]/W.iloc[k-1]-1)*100
        r21=(a.iloc[k+21]/a.iloc[k]-1)*100-cst(t); r63=(a.iloc[k+63]/a.iloc[k]-1)*100-cst(t)
        rows.append(dict(t=t,q=x.quarter,d=idx[k],timing=e.timing,yoy=x.yoy,acc=x.acc,re=re,r21=r21,x21=r21-bench(k,k+21),r63=r63,x63=r63-bench(k,k+63)))
D=pd.DataFrame(rows); print('quarter-filings:',len(D),'companies:',D.t.nunique(),D.groupby('t').size().to_dict())
def rep(g,lab):
    if len(g)<6: print(f"{lab:46s} n={len(g)}"); return
    y=g.d.dt.year
    print(f"{lab:46s} n={len(g):3d} | 21d: net {g.r21.mean():+5.2f} vsETF {g.x21.mean():+5.2f} beats {100*(g.x21>0).mean():3.0f}% t {g.x21.mean()/g.x21.std()*np.sqrt(len(g)):4.1f} | 63d: vsETF {g.x63.mean():+5.2f} beats {100*(g.x63>0).mean():3.0f}% | <2022 {g.x21[y<2022].mean():+5.2f} 2022+ {g.x21[y>=2022].mean():+5.2f}")
for lab,g in (('all',D),('ex LPP (fiscal-year shift)',D[D.t!='LPP']),('pre-session filings only',D[D.timing=='b'])):
    print('\n==',lab)
    rep(g,'all quarter-filings'); rep(g[g.acc>0],'acceleration > 0'); rep(g[g.acc>5],'acceleration > 5 pp'); rep(g[g.acc>10],'acceleration > 10 pp')
    rep(g[g.acc<=0],'acceleration <= 0'); rep(g[g.acc<-10],'acceleration < -10 pp'); rep(g[g.yoy>10],'y/y growth > 10%'); rep(g[g.yoy<0],'y/y growth < 0')
    rep(g[(g.acc>0)&(g.re>0)],'acc > 0 and positive reaction'); rep(g[(g.acc>0)&(g.re>=3)],'acc > 0 and reaction >= +3%'); rep(g[(g.acc<=0)&(g.re>=3)],'acc <= 0 and reaction >= +3%')
print('\ncorr(acc, reaction) %.2f; corr(acc, 21d vs ETF) %.2f; corr(acc, 63d vs ETF) %.2f'%(D.acc.corr(D.re),D.acc.corr(D.x21),D.acc.corr(D.x63)))
print('\nper company, acc > 0 vs <= 0 (21d vs ETF):'); print(D.groupby(['t',D.acc>0]).x21.agg(['count','mean']).round(1).unstack().to_string())
D.to_csv(os.path.join(H,'r14a_trades.csv'),index=False)
