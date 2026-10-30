import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
SC={'kupuj':5,'akumuluj':4,'trzymaj':3,'neutralnie':3,'neutralna':3,'redukuj':2,'sprzedaj':1}
d=pd.read_csv(os.path.join(H,'recs.csv')); d['date']=pd.to_datetime(d.pub_date.fillna(d.issue_date))
d['s']=d.rating.str.lower().map(SC); d=d.dropna(subset=['s','date']).sort_values('date')
d['ps']=d.groupby(['ticker','broker']).s.shift(1); d['pt']=d.groupby(['ticker','broker']).target.shift(1)
d['pdate']=d.groupby(['ticker','broker']).date.shift(1)
d['tchg']=(d.target/d.pt-1)*100; d['up']=(d.target/d.price_on_issue-1)*100
d=d[~d.date.isin(pd.to_datetime(['2023-12-11','2024-12-02','2025-11-30']))]   # BOS bulk dates
rng=np.random.default_rng(11)
rows=[]
for _,r in d.iterrows():
    t=r.ticker
    if t not in AD or t not in LIQ: continue
    i=idx.searchsorted(r.date)
    c=1.0 if t in L1 else 1.5
    rec=dict(t=t,d=r.date,s=r.s,ps=r.ps,tchg=r.tchg,up=r.up,gap=(r.date-r.pdate).days if pd.notna(r.pdate) else np.nan)
    for lag in (0,1,5,8):
        j=i+lag
        if j+21<len(idx) and np.isfinite(AD[t].iloc[j]) and np.isfinite(AD[t].iloc[j+21]):
            rec[f'x{lag}']=(AD[t].iloc[j+21]/AD[t].iloc[j]-1)*100-c-bench(j,j+21)
            rec[f'pre{lag}']=(AD[t].iloc[j]/AD[t].iloc[i-1]-1)*100-(W.iloc[j]/W.iloc[i-1]-1)*100 if i>0 else np.nan
    rows.append(rec)
D=pd.DataFrame(rows); print("usable recs:",len(D),"stocks",D.t.nunique())
def rep(m,lab):
    g=D[m]
    out=f"{lab:40s} n={len(g):4d}"
    for lag in (0,1,5,8):
        x=g[f'x{lag}'].dropna()
        if len(x)>3: out+=f" | lag{lag}: {x.mean():+5.2f}pp {100*(x>0).mean():3.0f}%"
    x=g['x5'].dropna(); y=g.loc[x.index,'d'].dt.year
    if len(x)>3: out+=f" | lag5 t {x.mean()/x.std()*np.sqrt(len(x)):4.1f} <2022 {x[y<2022].mean():+5.2f} 2022+ {x[y>=2022].mean():+5.2f}"
    print(out)
rep(D.s.notna(),"all recommendations")
rep(D.s==5,"buy"); rep(D.s<=2,"sell/reduce")
rep(D.s>D.ps,"UPGRADE (same broker)"); rep(D.s<D.ps,"DOWNGRADE (same broker)")
rep((D.s>D.ps)&(D.s>=4),"upgrade to buy/accumulate")
rep((D.s<D.ps)&(D.s<=3),"downgrade to hold or worse")
rep(D.tchg>=15,"target raised >=15%"); rep(D.tchg<=-15,"target cut >=15%")
rep((D.s==5)&(D.up>=30),"buy with upside >=30%")
rep((D.s<=2)&(D.up<=-15),"sell with downside >=15%")
print("pre-move between rec and lag5 entry (upgrades):",round(D[(D.s>D.ps)].pre5.mean(),2),"downgrades:",round(D[(D.s<D.ps)].pre5.mean(),2))
print("XTB short after target cut >=15% (absolute, cost ~0.9%):")
g=D[D.tchg<=-15]
for lag in (1,5):
    v=[]
    for _,r in g.iterrows():
        i=idx.searchsorted(r.d)+lag
        if i+21<len(idx): v.append(-((AD[r.t].iloc[i+21]/AD[r.t].iloc[i]-1)*100)-0.9)
    v=np.array(v); v=v[np.isfinite(v)]; print(f" lag{lag}: n={len(v)} {v.mean():+.2f}% wins {100*(v>0).mean():.0f}% t {v.mean()/v.std()*np.sqrt(len(v)):.1f}")
