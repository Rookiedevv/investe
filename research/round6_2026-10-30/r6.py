import os,sys,glob; sys.path.insert(0,os.path.dirname(__file__)); from lib import *
FD=R+'/research/prices_foreign/'; MD=R+'/data/prices/'
def ser(path):
    d=pd.read_csv(path,parse_dates=['date']).set_index('date')['adj_close']; d=d[~d.index.duplicated()]; return d
SPX=ser(MD+'SPX.csv'); DAX=ser(MD+'DAX.csv')
ETF=ser(MD+'ETFBW20TR.csv').reindex(idx).ffill()
def bench(i0,i1):
    if idx[i0]>=pd.Timestamp('2019-02-01'): r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100
    else: r=(W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
PAIRS={'TTWO':['CDR','11B','TEN','PLW','CIG'],'EA':['CDR','11B','TEN','PLW','CIG'],'UBI.PA':['CDR','11B','TEN','PLW','CIG'],
 'EMBRAC-B.ST':['CDR','11B','TEN','PLW','CIG'],'AMZN':['ALE'],'ZAL.DE':['ALE'],'FCX':['KGH'],'ANTO.L':['KGH'],
 'BP.L':['PKN'],'SHEL.L':['PKN'],'OMV.VI':['PKN'],'IGG.L':['XTB'],'PLUS.L':['XTB'],'CMCX.L':['XTB'],
 'INTRUM.ST':['KRU'],'HOFI.ST':['KRU'],
 'EBS.VI':['PKO','PEO','MBK','ING','MIL','ALR','EBP'],'OTP.BD':['PKO','PEO','MBK','ING','MIL','ALR'],'RBI.VI':['PKO','PEO','MBK','ING','MIL','ALR'],
 'KOMB.PR':['PKO','PEO','MBK','ING','MIL','ALR'],'INGA.AS':['ING'],'SAN.MC':['PKO','PEO','MBK'],'BNP.PA':['BNP'],'UCG.MI':['PEO'],'CBK.DE':['MBK'],
 'LKQ':['CAR','APR']}
US={'TTWO','EA','AMZN','FCX','LKQ'}
def peer_events(sym):
    p=ser(FD+sym+'.csv'); ix=(SPX if sym in US else DAX)
    df=pd.DataFrame({'p':p,'i':ix}).dropna(); r=df.pct_change()*100; ex=(r.p-r.i).dropna()
    sd=ex.rolling(250,min_periods=120).std().shift(1)
    q=ex.groupby(ex.index.to_period('Q'))
    out=[]
    for k,g in q:
        d=g.abs().idxmax(); v=ex[d]
        if np.isfinite(sd.get(d,np.nan)) and abs(v)>2*sd[d]: out.append((d,v,v/sd[d]))
    return out
def run(lag=0,H=21,thr=2.0):
    rows=[]
    for sym,pls in PAIRS.items():
        if not os.path.exists(FD+sym+'.csv'): continue
        for d,v,z in peer_events(sym):
            if abs(z)<thr: continue
            j=idx.searchsorted(d)+lag
            if j>=len(idx)-H or j<1: continue
            for t in pls:
                if t not in AD or not np.isfinite(AD[t].iloc[j]) or not np.isfinite(AD[t].iloc[j+H]): continue
                same=(AD[t].iloc[j]/AD[t].iloc[j-1]-1)*100-(W.iloc[j]/W.iloc[j-1]-1)*100
                r=(AD[t].iloc[j+H]/AD[t].iloc[j]-1)*100
                c=1.0 if t in L1 else (1.5 if t in L2 else 2.5)
                rows.append(dict(peer=sym,t=t,d=idx[j],v=v,z=z,same=same,r=r,c=c,b=bench(j,j+H)))
    return pd.DataFrame(rows)
def rep(d,lab,short=False):
    if d.empty: print(lab,'n=0'); return
    net=(-d.r-d.c+0.2-0.05) if short else (d.r-d.c)   # short: XTB markup instead of eMakler, swap ~0.05
    x=net-(0 if short else d.b) if not short else net   # longs vs ETF; shorts absolute
    y=d.d.dt.year
    t=x.mean()/x.std()*np.sqrt(len(x)) if len(x)>2 else np.nan
    print(f"{lab:48s} n={len(d):4d} net {net.mean():+5.2f}% | {'abs' if short else 'vsETF'} {x.mean():+5.2f} med {x.median():+5.2f} t {t:4.1f} win {100*(x>0).mean():3.0f}% | <2019 {x[y<2019].mean():+5.2f} 2019+ {x[y>=2019].mean():+5.2f}")
if __name__=='__main__':
    for lag in (0,1):
        D=run(lag)
        print(f"=== entry = Warsaw close {'same day as' if lag==0 else 'day after'} peer reaction ===")
        print("same-day corr peer move vs Polish move:",round(D[['v','same']].corr().iloc[0,1],2))
        for grp,g in [('ALL',D)]+list(D.groupby(D.peer.map(lambda s:{'TTWO':'gaming','EA':'gaming','UBI.PA':'gaming','EMBRAC-B.ST':'gaming','AMZN':'ecom','ZAL.DE':'ecom','FCX':'copper','ANTO.L':'copper','BP.L':'oil','SHEL.L':'oil','OMV.VI':'oil','IGG.L':'brokers','PLUS.L':'brokers','CMCX.L':'brokers','INTRUM.ST':'debt','HOFI.ST':'debt','LKQ':'carparts'}.get(s,'banks')))):
            rep(g[g.v>0],f"[{grp}] peer UP big -> buy, 21d vs ETF")
            rep(g[g.v<0],f"[{grp}] peer DOWN big -> XTB short 21d",short=True)
