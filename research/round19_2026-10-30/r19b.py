# Round 19b: new foreign series. (1) CHF/PLN moves -> CHF-mortgage banks (MIL, MBK, PKO, BNP) next month; (2) EPOL (US-listed MSCI Poland ETF,
# trades until 22:00 Warsaw) residual after the Warsaw close -> next-day WIG20 (W20 CFD costs); (3) Rotterdam coal futures momentum -> JSW / LWB next month.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
def load(sym): return pd.read_csv(R+f'/research/prices_foreign/{sym}.csv',parse_dates=['date']).set_index('date')
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
USD=pd.read_csv(R+'/data/prices/USDPLN.csv',parse_dates=['date']).set_index('date')['close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
chf=load('CHFPLN=X')['close'].reindex(idx).ffill()
print('== (1) CHF/PLN -> CHF-mortgage banks, 21-session hold after a 21-session CHF move, vs ETF (long) ==')
rows=[]
for i in range(300,len(idx)-22,5):
    m=(chf.iloc[i]/chf.iloc[i-21]-1)*100
    for t in ('MIL','MBK','PKO','BNP','PEO'):
        a=AD[t]
        if not(np.isfinite(a.iloc[i]) and np.isfinite(a.iloc[i+21])): continue
        r=(a.iloc[i+21]/a.iloc[i]-1)*100-1.0; rows.append(dict(t=t,d=idx[i],m=m,r=r,x=r-bench(i,i+21)))
D=pd.DataFrame(rows)
for t,g in D.groupby('t'): print(f"  {t}: corr(CHF 21d move, next-21d vs ETF) {g.m.corr(g.x):+.3f} | CHF up >3%: {g.x[g.m>3].mean():+5.2f} (n {(g.m>3).sum()}) | CHF down >3%: {g.x[g.m<-3].mean():+5.2f} (n {(g.m<-3).sum()}) | all {g.x.mean():+5.2f}")
# big CHF day (>= +2%) -> next 5 / 21 sessions
r1=chf.pct_change()*100; big=[i for i in range(300,len(idx)-22) if r1.iloc[i]>=1.5]
for t in ('MIL','MBK'):
    a=AD[t]; x5=[];x21=[]
    for i in big:
        if np.isfinite(a.iloc[i]) and np.isfinite(a.iloc[i+21]): x5.append((a.iloc[i+5]/a.iloc[i]-1)*100-(W.iloc[i+5]/W.iloc[i]-1)*100); x21.append((a.iloc[i+21]/a.iloc[i]-1)*100-(W.iloc[i+21]/W.iloc[i]-1)*100)
    print(f"  CHF/PLN day >= +1.5% (n {len(x5)}): {t} next 5 sessions vs WIG20 {np.mean(x5):+.2f}, next 21 {np.mean(x21):+.2f}")
print('\n== (2) EPOL residual after the Warsaw close -> next-day WIG20 ==')
ep=load('EPOL')['adj_close'].reindex(idx).ffill()
wusd=W/USD
re_ep=ep.pct_change()*100; re_w=wusd.pct_change()*100
resid=(re_ep-re_w)  # EPOL day return minus WIG20 (in USD) day return: roughly what happened 17:00-22:00 Warsaw plus noise
nxt=(W.shift(-1)/W-1)*100
Z=pd.DataFrame(dict(resid=resid,nxt=nxt)).dropna(); Z=Z[Z.index>='2015-01-01']
print('  corr(resid, next-day WIG20) %.3f  n=%d'%(Z.resid.corr(Z.nxt),len(Z)))
for lab,m in [('resid >= +1%',Z.resid>=1),('resid >= +1.5%',Z.resid>=1.5),('resid <= -1%',Z.resid<=-1),('resid <= -1.5%',Z.resid<=-1.5)]:
    g=Z[m]; print(f"  {lab:16s} n={len(g):4d} next-day WIG20 {g.nxt.mean():+5.2f}% (W20 CFD cost ~0.06) win {100*(g.nxt>0).mean():3.0f}% | 2022+ {g.nxt[g.index>='2022'].mean():+5.2f}")
Z['q']=pd.qcut(Z.resid,5,labels=False); print('  quintiles of resid -> next-day WIG20:',' '.join(f"q{q} {g.nxt.mean():+.2f}" for q,g in Z.groupby('q')))
# also: EPOL residual over the last 5 days -> next 5 days
print('\n== (3) Rotterdam coal futures (MTF=F) momentum -> JSW / LWB next month vs ETF ==')
coal=load('MTF=F')['close'].reindex(idx).ffill()
rows=[]
for i in range(300,len(idx)-22,5):
    if idx[i]>pd.Timestamp('2025-11-30'): break
    m1=(coal.iloc[i]/coal.iloc[i-21]-1)*100; m3=(coal.iloc[i]/coal.iloc[i-63]-1)*100
    for t in ('JSW','LWB','PGE','TPE','ENA'):
        a=AD[t]
        if not(np.isfinite(a.iloc[i]) and np.isfinite(a.iloc[i+21])): continue
        r=(a.iloc[i+21]/a.iloc[i]-1)*100-1.0; rows.append(dict(t=t,d=idx[i],m1=m1,m3=m3,r=r,x=r-bench(i,i+21),sh=-(a.iloc[i+21]/a.iloc[i]-1)*100-0.96))
D=pd.DataFrame(rows)
for t,g in D.groupby('t'):
    print(f"  {t}: corr(coal 1m,{'next-month vs ETF'}) {g.m1.corr(g.x):+.3f} corr(coal 3m) {g.m3.corr(g.x):+.3f} | coal 1m up >10%: {g.x[g.m1>10].mean():+5.2f} (n {(g.m1>10).sum()}) | coal 1m down >10%: {g.x[g.m1<-10].mean():+5.2f} (n {(g.m1<-10).sum()}), XTB short {g.sh[g.m1<-10].mean():+5.2f}")
