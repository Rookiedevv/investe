# Round 12a: results drift for AFTER-session and DURING-session filings (next-day / same-day entry), plus negative-reaction shorts.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
from cal_timing import events
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
def cst(t): return 1.0 if t in L1 else (1.5 if t in L2 else 2.5)
rng=np.random.default_rng(12); RAND={}
def own_rand(t,k=200):
    s=AD[t].dropna(); a=idx.get_loc(s.index[0]); b=idx.get_loc(s.index[-1])-21; v=[]
    for _ in range(k):
        i=int(rng.integers(a,b)); v.append((AD[t].iloc[i+21]/AD[t].iloc[i]-1)*100-cst(t)-bench(i,i+21))
    return float(np.nanmean(v))
E=events(); E=E[E.date>='2016-01-01']
VOLREL=VO/VO.rolling(60,min_periods=20).median().shift(1)
rows=[]
for t,g in E.groupby('t'):
    if t not in AD: continue
    alli=[idx.searchsorted(d) for d in g.date]
    for (_,e),i in zip(g.iterrows(),alli):
        if i>=len(idx) or idx[i]!=e.date or e.timing in ('u','n'): continue
        if any(0<i-j<=30 for j in alli): continue                      # not first news of the quarter
        k = i+1 if e.timing=='a' else i                                  # reaction day
        if k<1 or k+21>=len(idx): continue
        a=AD[t]
        if not (np.isfinite(a.iloc[k-1]) and np.isfinite(a.iloc[k]) and np.isfinite(a.iloc[k+21])): continue
        re=(a.iloc[k]/a.iloc[k-1]-1)*100-(W.iloc[k]/W.iloc[k-1]-1)*100
        r=(a.iloc[k+21]/a.iloc[k]-1)*100-cst(t)
        sh=-(a.iloc[k+21]/a.iloc[k]-1)*100-(0.6+0.3+0.7*21/252)            # XTB short: markup both sides + spread + swap ≈ 0.96%
        if t not in RAND: RAND[t]=own_rand(t)
        rows.append(dict(t=t,d=idx[k],timing=e.timing,prelim=e.prelim,re=re,r=r,sh=sh,b=bench(k,k+21),ctl=RAND[t],
                         vr=VOLREL[t].iloc[k] if t in VOLREL else np.nan,liq='L1' if t in L1 else ('L2' if t in L2 else 'thin')))
df=pd.DataFrame(rows); df['x']=df.r-df.b
print(f"first-news filings with a reaction day: {len(df)} ({df.t.nunique()} stocks); by timing:",df.timing.value_counts().to_dict())
def rep(g,lab):
    if len(g)<5: print(f"{lab:52s} n={len(g)}"); return
    y=g.d.dt.year; tt=g.x.mean()/g.x.std()*np.sqrt(len(g))
    print(f"{lab:52s} n={len(g):3d} net {g.r.mean():+5.2f}% | vs ETF {g.x.mean():+5.2f}pp med {g.x.median():+5.2f} t {tt:4.1f} beats {100*(g.x>0).mean():3.0f}% | <2022 {g.x[y<2022].mean():+5.2f} 2022+ {g.x[y>=2022].mean():+5.2f} | excess {g.x.mean()-g.ctl.mean():+5.2f}")
for tm,name in (('b','pre-session (control: round 9)'),('a','AFTER session -> next-day entry'),('d','DURING session -> same-day entry')):
    print('\n==',name)
    for lo,hi in ((3,6),(2,6),(3,99),(6,99),(0,3),(-3,0),(-99,-3)):
        for liq,sel in (('L1',df.liq=='L1'),('L1+L2',df.liq!='thin'),('thin',df.liq=='thin')):
            rep(df[(df.timing==tm)&sel&(df.re>=lo)&(df.re<hi)],f"reaction {lo}..{hi}% [{liq}]")
print('\n== pooled pre + after (first news), L1')
for lo,hi in ((3,6),(2,6),(6,99),(-99,-3)):
    rep(df[(df.timing.isin(['b','a']))&(df.liq=='L1')&(df.re>=lo)&(df.re<hi)],f"reaction {lo}..{hi}%")
print('\n== after-session +3..6 L1: per stock / per year')
g=df[(df.timing=='a')&(df.liq=='L1')&(df.re>=3)&(df.re<6)]
print(g.groupby('t').x.agg(['count','mean']).round(1).T.to_string())
print(g.groupby(g.d.dt.year).x.agg(['count','mean']).round(1).T.to_string())
print('\n== prelim vs full report (pre+after, L1, +3..6)')
for p in (True,False):
    rep(df[(df.timing.isin(['b','a']))&(df.liq=='L1')&(df.re>=3)&(df.re<6)&(df.prelim==p)],f"prelim={p}")
print('\n== volume filter on the reaction day (pre+after, L1, +3..6): vol / 60d median')
g=df[(df.timing.isin(['b','a']))&(df.liq=='L1')&(df.re>=3)&(df.re<6)]
for lo,hi in ((0,1.5),(1.5,2.5),(2.5,99)):
    rep(g[(g.vr>=lo)&(g.vr<hi)],f"vol ratio {lo}..{hi}")
print('\n== NEGATIVE reactions -> XTB short (hold 21), L1, pre+after')
def reps(g,lab):
    if len(g)<5: print(lab,'n',len(g)); return
    y=g.d.dt.year; tt=g.sh.mean()/g.sh.std()*np.sqrt(len(g))
    print(f"{lab:52s} n={len(g):3d} short net {g.sh.mean():+5.2f}% med {g.sh.median():+5.2f} t {tt:4.1f} win {100*(g.sh>0).mean():3.0f}% | <2022 {g.sh[y<2022].mean():+5.2f} 2022+ {g.sh[y>=2022].mean():+5.2f}")
g=df[(df.timing.isin(['b','a']))&(df.liq=='L1')]
for lo,hi in ((-99,-6),(-6,-3),(-99,-3),(-3,-1)):
    reps(g[(g.re>=lo)&(g.re<hi)],f"reaction {lo}..{hi}% short")
    for tm in ('b','a'): reps(g[(g.re>=lo)&(g.re<hi)&(g.timing==tm)],f"   timing {tm}")
df.to_csv(os.path.join(H,'r12a_trades.csv'),index=False)
