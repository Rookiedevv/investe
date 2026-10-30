import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); from lib import *
MD=R+'/data/prices/'
ETF=pd.read_csv(MD+'ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
def basket(ts,i0,i1,cost=1.0):
    rr=[(AD[t].iloc[i1]/AD[t].iloc[i0]-1)*100 for t in ts if np.isfinite(AD[t].iloc[i0]) and np.isfinite(AD[t].iloc[i1])]
    return np.mean(rr)-cost if rr else np.nan
RET='DNP LPP PCO ALE ZAB EUR'.split(); BANKS='PKO PEO MBK ALR ING MIL EBP BHW'.split()
def rep(rows,lab):
    d=pd.DataFrame(rows,columns=['d','r','b']).dropna()
    if len(d)<3: print(f"{lab:58s} n={len(d)}"); return
    x=d.r-d.b; y=d.d.dt.year; t=x.mean()/x.std()*np.sqrt(len(x))
    print(f"{lab:58s} n={len(d):3d} vs ETF {x.mean():+5.2f}pp med {x.median():+5.2f} t {t:4.1f} beats {100*(x>0).mean():3.0f}% | <2021 {x[y<2021].mean():+5.2f} 2021+ {x[y>=2021].mean():+5.2f}")
for fn,lab in (('retail_sales.csv','RETAIL SALES'),('wages.csv','WAGES')):
    S=pd.read_csv(os.path.join(H,fn),parse_dates=['release_date'])
    S['surp']=S.yoy-S.consensus; S['acc']=S.yoy-S.yoy.shift(1).rolling(3).mean()
    print(f"== {lab} (release 10:00, entry at release-day close, hold 21) ==")
    for col,thr in (('surp',1.0),('surp',2.0),('acc',2.0)):
        for sgn,nm in ((1,'above'),(-1,'below')):
            for grp,ts in (('retailers',RET),('banks',BANKS),('WIG20 ETF vs deposit',None)):
                rows=[]
                for _,s in S.iterrows():
                    v=s[col]
                    if not np.isfinite(v) or sgn*v<thr: continue
                    i=idx.searchsorted(s.release_date)
                    if i+21>=len(idx): continue
                    if ts is None: rows.append((idx[i],bench(i,i+21),0.45))
                    else: rows.append((idx[i],basket(ts,i,i+21),bench(i,i+21)))
                rep(rows,f"{col} {nm} {'+' if sgn>0 else '-'}{thr}: {grp}")
    # same-day reaction check
    rr=[]
    for _,s in S.iterrows():
        i=idx.searchsorted(s.release_date)
        if np.isfinite(s.surp) and i<len(idx): rr.append((s.surp,basket(RET,i-1,i,0)-(W.iloc[i]/W.iloc[i-1]-1)*100))
    a=np.array(rr); print("same-day corr(surprise, retailers vs WIG20):",round(np.corrcoef(a.T)[0,1],2))
