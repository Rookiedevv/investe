import pandas as pd, numpy as np, glob, os
import pathlib; R=str(pathlib.Path(__file__).resolve().parents[2])
def load():
    P={}
    for f in glob.glob(R+'/research/prices/*.csv')+glob.glob(R+'/data/prices/*.csv'):
        t=os.path.basename(f)[:-4]
        if t.startswith('_') or t in ('WIG','WIG20','FW20','SPX','DAX','NDQ','VIX','EURPLN','USDPLN','BRENT','ETFBW20TR'): continue
        d=pd.read_csv(f,parse_dates=['date']).dropna(subset=['close']).set_index('date')
        d=d[~d.index.duplicated()]
        if t in P and len(P[t])>len(d): continue
        P[t]=d
    w=pd.read_csv(R+'/data/prices/WIG20.csv',parse_dates=['date']).set_index('date')['close']
    return P,w
P,W=load()
TICK=sorted(P)
CL=pd.DataFrame({t:P[t]['close'] for t in TICK})
AD=pd.DataFrame({t:P[t]['adj_close'] for t in TICK})
VO=pd.DataFrame({t:P[t]['volume'] for t in TICK})
idx=CL.index.union(W.index); idx=idx[idx>='2011-01-01']
CL,AD,VO=CL.reindex(idx),AD.reindex(idx),VO.reindex(idx)
W=W.reindex(idx).ffill()
TURN=(CL*VO).rolling(60,min_periods=20).median()
def cost(turn):
    return np.select([turn>30e6,turn>10e6,turn>3e6,turn>1e6],[0.9,1.0,1.3,2.0],2.7)
def trade(t,i0,i1,short=False):
    a=AD[t]
    p0,p1=a.iloc[i0],a.iloc[i1]
    if not(np.isfinite(p0) and np.isfinite(p1)) or p0<=0: return None
    r=(p1/p0-1)*100; wr=(W.iloc[i1]/W.iloc[i0]-1)*100
    tv=TURN[t].iloc[i0]; c=float(cost(tv)) if np.isfinite(tv) else 2.7
    if short:
        c=0.6+float(cost(tv))-0.78+0.7*(i1-i0)/252  # XTB markup instead of eMakler commission + swap
        r=-r; wr=-wr
    return dict(t=t,d=idx[i0],r=r-c,ex=r-wr,turn=tv,n=i1-i0)
def summ(rows,label):
    df=pd.DataFrame([x for x in rows if x])
    if df.empty: print(label,'n=0'); return df
    y=df.d.dt.year
    a=df[y<2019].r.mean() if (y<2019).any() else np.nan; b=df[y>=2019].r.mean()
    t=df.r.mean()/df.r.std()*np.sqrt(len(df)) if len(df)>2 else np.nan
    print(f"{label:58s} n={len(df):4d} net {df.r.mean():+5.1f}% med {df.r.median():+5.1f} vsW20 {df.ex.mean():+5.1f}pp t {t:4.1f} win {100*(df.r>0).mean():3.0f}% <2019 {a:+5.1f} 2019+ {b:+5.1f}")
    return df
rng=np.random.default_rng(1)
def placebo(df,hold,short=False,k=20):
    rows=[]
    for _,x in df.iterrows():
        s=AD[x.t].dropna(); ii=[idx.get_loc(d) for d in s.index]
        lo=ii[0]; hi=ii[-1]-hold
        for _ in range(k):
            i0=int(rng.integers(lo,hi)); rows.append(trade(x.t,i0,i0+hold,short))
    return pd.DataFrame([r for r in rows if r])
L1=set('PKO PEO PZU KGH PKN ALE DNP CDR LPP XTB ZAB PCO PGE ASB ACP TPE MBK ALR KTY BDX KRU OPL JSW MIL SNT CPS ING ENA APR CAR EBP DIA'.split())
L2=set('BHW CBF PXM VRG DOM LBW RBW TEN 11B CRI'.split())
LIQ=L1|L2
def cost(turn): return 1.0
def trade(t,i0,i1,short=False):
    if t not in LIQ: return None
    a=AD[t]; p0,p1=a.iloc[i0],a.iloc[i1]
    if not(np.isfinite(p0) and np.isfinite(p1)) or p0<=0: return None
    r=(p1/p0-1)*100; wr=(W.iloc[i1]/W.iloc[i0]-1)*100
    c=1.0 if t in L1 else 1.5
    if short: c=c-0.2+0.7*(i1-i0)/252; r=-r; wr=-wr
    return dict(t=t,d=idx[i0],r=r-c,ex=r-wr,n=i1-i0)
