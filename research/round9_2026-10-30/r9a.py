import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); from lib import *
from pre_session import B, ALL
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
def D(s): return sorted(pd.to_datetime(['20'+x for x in s.split()]))
rng=np.random.default_rng(9)
def own_rand(t,k=200):
    s=AD[t].dropna(); a=idx.get_loc(s.index[0]); b=idx.get_loc(s.index[-1])-21; v=[]
    for _ in range(k):
        i=int(rng.integers(a,b)); v.append((AD[t].iloc[i+21]/AD[t].iloc[i]-1)*100-(1.0 if t in L1 else 1.5)-bench(i,i+21))
    v=np.array(v); return np.nanmean(v)
RAND={}
rows=[]
for t,s in B.items():
    if t not in AD: continue
    alld=[idx.searchsorted(d) for d in D(ALL[t])] if t in ALL else []
    for d in D(s):
        i=idx.searchsorted(d)
        if i>=len(idx)-21 or i<1 or idx[i]!=d: continue
        if any(0<i-j<=30 for j in alld): continue            # earlier release of the same quarter within 30 sessions -> not first news
        re=(AD[t].iloc[i]/AD[t].iloc[i-1]-1)*100-(W.iloc[i]/W.iloc[i-1]-1)*100
        c=1.0 if t in L1 else (1.5 if t in L2 else 2.5)
        r=(AD[t].iloc[i+21]/AD[t].iloc[i]-1)*100-c
        if t not in RAND: RAND[t]=own_rand(t)
        rows.append(dict(t=t,d=idx[i],re=re,r=r,b=bench(i,i+21),ctl=RAND[t],liq='L1' if t in L1 else ('L2' if t in L2 else 'thin')))
df=pd.DataFrame(rows); df['x']=df.r-df.b
print(f"pre-session first-news releases: {len(df)} ({df.t.nunique()} stocks)")
def rep(g,lab):
    if len(g)<3: print(lab,'n',len(g)); return
    y=g.d.dt.year; tt=g.x.mean()/g.x.std()*np.sqrt(len(g))
    print(f"{lab:44s} n={len(g):3d} net {g.r.mean():+5.2f}% | vs ETF {g.x.mean():+5.2f}pp med {g.x.median():+5.2f} t {tt:4.1f} beats {100*(g.x>0).mean():3.0f}% | <2022 {g.x[y<2022].mean():+5.2f} 2022+ {g.x[y>=2022].mean():+5.2f} | excess {g.x.mean()-g.ctl.mean():+5.2f}")
for lo,hi in ((2,6),(3,6),(2,99),(6,99),(0,2),(-2,0),(-99,-2)):
    for liq,sel in (('L1',df.liq=='L1'),('L1+L2',df.liq!='thin')):
        rep(df[sel&(df.re>=lo)&(df.re<hi)],f"reaction {lo}..{hi}% [{liq}]")
g=df[(df.liq=='L1')&(df.re>=2)&(df.re<6)]
print(g.groupby('t').x.agg(['count','mean']).round(1).T.to_string())
print(g.groupby(g.d.dt.year).x.agg(['count','mean']).round(1).T.to_string())
