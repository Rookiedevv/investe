import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
def eff(d,timing):
    j=idx.searchsorted(pd.Timestamp(d))
    if j<len(idx) and idx[j]==pd.Timestamp(d) and timing in('b','d','before','during'): return j
    return j if (j<len(idx) and idx[j]!=pd.Timestamp(d)) else j+1
def ret(t,i0,i1,c): return (AD[t].iloc[i1]/AD[t].iloc[i0]-1)*100-c
rng=np.random.default_rng(5)
def own_random(t,n,c,k=3000):
    s=AD[t].dropna(); a=idx.get_loc(s.index[0]); b=idx.get_loc(s.index[-1])-n
    v=[]
    for _ in range(k):
        i=int(rng.integers(a,b)); v.append(ret(t,i,i+n,c)-bench(i,i+n))
    v=np.array(v); v=v[np.isfinite(v)]; return v.mean(),(v>0).mean()*100
def rep(rows,lab):
    d=pd.DataFrame(rows,columns=['t','d','r','b','n']).dropna()
    x=d.r-d.b; y=d.d.dt.year; tt=x.mean()/x.std()*np.sqrt(len(x))
    # survivorship control: same stocks, same hold lengths, random dates
    ctl=[own_random(t,int(n),1.5 if t in('ASB',) else 1.0,300)[0] for t,n in zip(d.t,d.n)]
    print(f"{lab:46s} n={len(d):3d} net {d.r.mean():+5.2f}% | vs ETF {x.mean():+5.2f}pp med {x.median():+5.2f} t {tt:4.1f} beats ETF {100*(x>0).mean():3.0f}% | <2022 {x[y<2022].mean():+5.2f} 2022+ {x[y>=2022].mean():+5.2f} | same stock random {np.mean(ctl):+5.2f} -> excess {x.mean()-np.mean(ctl):+5.2f}")
    return d
# 1. Car parts
C=pd.read_csv(R+'/data/carparts_sales.csv'); C['date']=pd.to_datetime(C.date)
for thr in (0,5,10):
    rows=[]
    for t in ('CAR','APR'):
        s=C[C.ticker==t].copy(); s['yoy_pct']=s.yoy_pct.fillna((s.sales_pln_m/s.sales_prev_year_pln_m-1)*100); s=s.dropna(subset=['yoy_pct']).sort_values('date').drop_duplicates('period',keep='first').reset_index(drop=True)
        s['acc']=s.yoy_pct-s.yoy_pct.shift(1).rolling(3).mean()
        for k in range(3,len(s)-1):
            if not s.acc[k]>thr: continue
            i0=eff(s.date[k],s.session_timing[k][0])+1; i1=eff(s.date[k+1],s.session_timing[k+1][0])
            if i1>=len(idx) or i1<=i0: continue
            rows.append((t,idx[i0],ret(t,i0,i1,1.0),bench(i0,i1),i1-i0))
    rep(rows,f"Car parts accel >{thr}pp (CAR+APR)")
# 2. Asbis
S=pd.read_csv(os.path.join(H,'asbis_sales.csv'),parse_dates=['date'])
S['acc']=S.yoy-S.yoy.shift(1).rolling(3).mean()
for thr in (0,5):
    rows=[]
    for k in range(3,len(S)-1):
        if not S.acc[k]>thr: continue
        i0=eff(S.date[k],S.timing[k]); i1=eff(S.date[k+1],S.timing[k+1])
        if i1>=len(idx) or i1<=i0: continue
        rows.append(('ASB',idx[i0],ret('ASB',i0,i1,1.5),bench(i0,i1),i1-i0))
    rep(rows,f"Asbis accel >{thr}pp")
# 3. Biedronka -> Dino
B=pd.read_csv(os.path.join(H,'biedronka_lfl.csv'),parse_dates=['date'])
for thr in (0,2):
    rows=[]
    for k in range(1,len(B)):
        if not B.lfl[k]-B.lfl[k-1]>thr: continue
        i0=eff(B.date[k],B.timing[k])
        if B.timing[k]=='a': i0=idx.searchsorted(B.date[k],side='right')
        if i0+21>=len(idx) or not np.isfinite(AD['DNP'].iloc[i0]): continue
        rows.append(('DNP',idx[i0],ret('DNP',i0,i0+21,1.0),bench(i0,i0+21),21))
    rep(rows,f"Biedronka LFL improved >{thr}pp -> Dino 21d")
# 4. PZU results-day reaction
from cal import C as CAL
rows=[]
for d in sorted(pd.to_datetime(['20'+x for x in CAL['PZU'].split()])):
    i=idx.searchsorted(d)
    if i+21>=len(idx) or i<1 or idx[i]!=d: continue
    re=(AD['PZU'].iloc[i]/AD['PZU'].iloc[i-1]-1)*100-(W.iloc[i]/W.iloc[i-1]-1)*100
    if re>=2: rows.append(('PZU',idx[i],ret('PZU',i,i+21,1.0),bench(i,i+21),21))
rep(rows,"PZU results day >= +2pp vs WIG20")
# 5. Results drift (pre-session habit names only: PZU, PKN, PCO, ALE, BDX)
rows=[]
for t in ('PZU','PKN','PCO','ALE','BDX'):
    last=-99
    for d in sorted(pd.to_datetime(['20'+x for x in CAL[t].split()])):
        i=idx.searchsorted(d)
        if i+21>=len(idx) or i<1 or idx[i]!=d or i-last<30: continue
        re=(AD[t].iloc[i]/AD[t].iloc[i-1]-1)*100-(W.iloc[i]/W.iloc[i-1]-1)*100
        if 2<=re<=6: rows.append((t,idx[i],ret(t,i,i+21,1.0),bench(i,i+21),21)); last=i
rep(rows,"Results drift +2..6% (PZU PKN PCO ALE BDX)")
