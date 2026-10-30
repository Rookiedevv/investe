import os,sys; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
D=R+'/data/prices/'
def m(t): return pd.read_csv(D+t+'.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
ETF=m('ETFBW20TR'); DAX=m('DAX'); SPX=m('SPX'); VIX=m('VIX'); USD=m('USDPLN'); EURP=m('EURPLN')
# ETF-like benchmark: real ETF from 2019, else WIG20 + 3.5%/yr dividends; minus eMakler 0.78 round trip
def bench(i0,i1):
    if idx[i0]>=pd.Timestamp('2019-02-01') and np.isfinite(ETF.iloc[i0]):
        r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100
    else: r=(W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
def basket(ts,i0,i1,cost=1.0):
    rr=[]
    for t in ts:
        a=AD[t]; p0,p1=a.iloc[i0],a.iloc[i1]
        if np.isfinite(p0) and np.isfinite(p1) and p0>0: rr.append((p1/p0-1)*100)
    return (np.mean(rr)-cost) if rr else np.nan
def rep(rows,lab):
    d=pd.DataFrame(rows,columns=['d','r','b']).dropna()
    if d.empty: print(lab,'n=0'); return
    x=d.r-d.b; y=d.d.dt.year
    a=x[y<2019].mean() if (y<2019).any() else np.nan; c=x[y>=2019].mean()
    t=x.mean()/x.std()*np.sqrt(len(x)) if len(x)>2 else np.nan
    print(f"{lab:62s} n={len(d):3d} net {d.r.mean():+5.2f}% | vs ETF {x.mean():+5.2f}pp med {x.median():+5.2f} t {t:4.1f} beats ETF {100*(x>0).mean():3.0f}% | <2019 {a:+5.2f} 2019+ {c:+5.2f}")
me=pd.Series(idx,index=idx).resample('ME').last().values
ME=[idx.get_loc(pd.Timestamp(d)) for d in me]; ME=[i for i in ME if i>=260]
pairs=list(zip(ME[:-1],ME[1:]))
BANKS='PKO PEO MBK ALR ING MIL EBP BHW'.split(); UTIL='PGE TPE ENA'.split()
EXP='KGH KTY JSW'.split()
print("== A. Zloty moves (month-end signal, hold next month) ==")
for lab,S in (("USD/PLN",USD),("EUR/PLN",EURP)):
  for thr in (2,3):
    weak=[(idx[i],basket(['__'],i,j) ,0) for i,j in []]
    rowsW=[];rowsS=[];rowsEW=[];rowsES=[]
    for i,j in pairs:
        ch=(S.iloc[i]/S.iloc[i-21]-1)*100
        if not np.isfinite(ch): continue
        b=bench(i,j)
        if ch>thr: rowsEW.append((idx[i],basket(EXP,i,j),b)); rowsW.append((idx[i],b+0.78-0.78,0.45))
        if ch<-thr: rowsES.append((idx[i],basket(EXP,i,j),b)); rowsS.append((idx[i],b,0.45))
    rep(rowsEW,f"{lab} +{thr}% (PLN weak): exporters KGH/KTY/JSW vs ETF")
    rep(rowsES,f"{lab} -{thr}% (PLN strong): exporters vs ETF")
    rep(rowsS,f"{lab} -{thr}% (PLN strong): WIG20 ETF vs deposit")
    rep(rowsW,f"{lab} +{thr}% (PLN weak): WIG20 ETF vs deposit")
allm=[(idx[i],bench(i,j),0.45) for i,j in pairs]; rep(allm,"   reference: any month, WIG20 ETF vs deposit")
print("== B. WIG20 lagging DAX / S&P 500 over the past month ==")
for lab,S in (("DAX",DAX),("SPX",SPX)):
  for thr in (3,5):
    r1=[];r2=[];r3=[]
    for i,j in pairs:
        gap=((W.iloc[i]/W.iloc[i-21])-(S.iloc[i]/S.iloc[i-21]))*100
        if gap<-thr:
            r1.append((idx[i],bench(i,j),0.45)); r2.append((idx[i],basket(BANKS,i,j),bench(i,j)))
        if gap>thr: r3.append((idx[i],bench(i,j),0.45))
    rep(r1,f"WIG20 lags {lab} by >{thr}pp: WIG20 ETF next month vs deposit")
    rep(r2,f"WIG20 lags {lab} by >{thr}pp: banks next month vs ETF")
    rep(r3,f"WIG20 beats {lab} by >{thr}pp: WIG20 ETF next month vs deposit")
print("== C. VIX spike then retreat ==")
for pk,ret in ((30,0.2),(25,0.2),(30,0.3)):
    r1=[];r2=[];last=-99
    for i in range(30,len(idx)-22):
        win=VIX.iloc[i-10:i+1]; p=win.max()
        if p>pk and VIX.iloc[i]<=p*(1-ret) and VIX.iloc[i-1]>p*(1-ret) and i-last>21:
            last=i; r1.append((idx[i],bench(i,i+21),0.45*1)); r2.append((idx[i],basket(BANKS,i,i+21),bench(i,i+21)))
    rep(r1,f"VIX peak>{pk} then -{int(ret*100)}% within 10d: WIG20 ETF 21d vs deposit")
    rep(r2,f"   same: banks 21d vs ETF")
print("== D. Sector rotation (month-end, hold top sector next month) ==")
SEC={'banks':BANKS,'util':UTIL,'commod':'KGH JSW PKN LWB'.split(),'consumer':'LPP DNP PCO ALE ZAB EUR'.split(),
     'tech/game':'CDR 11B TEN ACP'.split(),'fin':'PZU XTB KRU'.split(),'constr':'BDX MRB DOM'.split()}
for lb,skip in ((63,0),(126,21),(21,0)):
    rows=[];prev=None;rowsBot=[]
    for i,j in pairs:
        sc={}
        for s,ts in SEC.items():
            v=[AD[t].iloc[i-skip]/AD[t].iloc[i-lb]-1 for t in ts if np.isfinite(AD[t].iloc[i-lb]) and np.isfinite(AD[t].iloc[i-skip])]
            if v: sc[s]=np.mean(v)
        if len(sc)<5: continue
        top=max(sc,key=sc.get); bot=min(sc,key=sc.get)
        c=1.0 if top!=prev else 0.0; prev=top
        rows.append((idx[i],basket(SEC[top],i,j,c),bench(i,j)))
        rowsBot.append((idx[i],basket(SEC[bot],i,j,1.0),bench(i,j)))
    rep(rows,f"top sector by {lb}d return (skip {skip}d), hold 1 month vs ETF")
    rep(rowsBot,f"   bottom sector (reversal) vs ETF")
print("== E. Turn of year: mid caps vs ETF ==")
MID=[t for t in LIQ if t not in 'PKO PEO PZU KGH PKN ALE DNP CDR LPP'.split()]
rows=[];rows2=[]
for y in range(2014,2026):
    i0=idx.searchsorted(pd.Timestamp(f'{y}-12-15')); i1=idx.searchsorted(pd.Timestamp(f'{y+1}-01-31'),side='right')-1
    i2=idx.searchsorted(pd.Timestamp(f'{y}-12-31'),side='right')-1
    rows.append((idx[i0],basket(MID,i0,i1),bench(i0,i1))); rows2.append((idx[i2],basket(MID,i2,i1),bench(i2,i1)))
rep(rows,"mid caps 15 Dec -> end Jan vs ETF"); rep(rows2,"mid caps 31 Dec -> end Jan vs ETF")
