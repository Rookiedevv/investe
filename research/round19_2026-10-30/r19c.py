# Round 19c: follow-ups on the three round-19b leads with clean (non-overlapping) samples and tradable costs.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
def load(sym): return pd.read_csv(R+f'/research/prices_foreign/{sym}.csv',parse_dates=['date']).set_index('date')
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
USD=pd.read_csv(R+'/data/prices/USDPLN.csv',parse_dates=['date']).set_index('date')['close'].reindex(idx).ffill()
FW=pd.read_csv(R+'/data/prices/FW20.csv',parse_dates=['date']).set_index('date').reindex(idx)
SPX=pd.read_csv(R+'/data/prices/SPX.csv',parse_dates=['date']).set_index('date')['close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
print('== A. CHF/PLN jump days -> short CHF-mortgage banks on XTB (cost 0.96% + swap), non-overlapping, 2015-26 ==')
chf=load('CHFPLN=X')['close'].reindex(idx).ffill(); r1=chf.pct_change()*100
for thr in (1.0,1.5,2.0):
    days=[];last=-99
    for i in range(300,len(idx)-22):
        if r1.iloc[i]>=thr and i-last>21: days.append(i); last=i
    for t in ('MIL','MBK','PKO','BNP'):
        a=AD[t]; out=f"  CHF day >= {thr:.1f}% (n={len(days):2d}) {t}:"
        for h in (5,10,21):
            x=[];xs=[]
            for i in days:
                if np.isfinite(a.iloc[i]) and np.isfinite(a.iloc[i+h]):
                    rr=(a.iloc[i+h]/a.iloc[i]-1)*100; x.append(rr-(W.iloc[i+h]/W.iloc[i]-1)*100); xs.append(-rr-0.96-0.7*h/252)
            x=np.array(x); xs=np.array(xs); out+=f" h{h:2d} vsWIG {x.mean():+5.2f} short net {xs.mean():+5.2f} win {100*(xs>0).mean():3.0f}% |"
        print(out)
    print('   dates:',', '.join(idx[i].strftime('%Y-%m-%d') for i in days) if thr==1.5 else '')
print('\n== B. EPOL residual (EPOL day return minus WIG20-in-USD day return) -> next day, split into FW20 opening gap and open-to-close ==')
ep=load('EPOL')['adj_close'].reindex(idx).ffill(); wusd=W/USD
resid=(ep.pct_change()-wusd.pct_change())*100
spx_late=None
gap=(FW.open.shift(-1)/FW.close-1)*100          # FW20 close t -> FW20 open t+1 (08:45)
oc=(FW.close.shift(-1)/FW.open.shift(-1)-1)*100   # FW20 open t+1 -> close t+1
cc=(W.shift(-1)/W-1)*100
Z=pd.DataFrame(dict(resid=resid,gap=gap,oc=oc,cc=cc,spx=SPX.pct_change()*100)).dropna(); Z=Z[(Z.index>='2015-01-01')]
print('  n=%d corr(resid,next cc) %.3f corr(resid,gap) %.3f corr(resid,open->close) %.3f ; corr(S&P same day, next cc) %.3f'%(len(Z),Z.resid.corr(Z.cc),Z.resid.corr(Z.gap),Z.resid.corr(Z.oc),Z.spx.corr(Z.cc)))
for lab,m in [('resid >= +1.5%',Z.resid>=1.5),('resid <= -1.5%',Z.resid<=-1.5),('resid >= +1%',Z.resid>=1),('resid <= -1%',Z.resid<=-1)]:
    g=Z[m]; y=g.index.year
    print(f"  {lab:16s} n={len(g):3d} next cc {g.cc.mean():+5.2f} | FW20 gap {g.gap.mean():+5.2f} | open->close {g.oc.mean():+5.2f} (win {100*(g.oc>0).mean():3.0f}%) | o->c 2015-18 {g.oc[y<2019].mean():+5.2f} 2019-22 {g.oc[(y>=2019)&(y<2023)].mean():+5.2f} 2023+ {g.oc[y>=2023].mean():+5.2f}")
# is the residual just the S&P after 17:00? control: S&P day return (close 22:00) alone
Z['spx_q']=pd.qcut(Z.spx,5,labels=False); print('  S&P day-return quintiles -> next-day FW20 open->close:',' '.join(f"q{q} {g.oc.mean():+.2f}" for q,g in Z.groupby('spx_q')))
Z['rq']=pd.qcut(Z.resid,5,labels=False); print('  EPOL-resid quintiles -> next-day FW20 open->close:',' '.join(f"q{q} {g.oc.mean():+.2f}" for q,g in Z.groupby('rq')))
print('\n== C. coal futures (MTF=F) month-end momentum -> JSW / LWB next month (non-overlapping, 2015-2025) ==')
coal=load('MTF=F')['close'].reindex(idx).ffill()
me=[i for i in range(300,len(idx)-22) if idx[i].month!=idx[i+1].month and idx[i]<=pd.Timestamp('2025-11-30')]
for t in ('JSW','LWB'):
    rows=[]
    for i in me:
        a=AD[t]
        if not(np.isfinite(a.iloc[i]) and np.isfinite(a.iloc[i+21]) and np.isfinite(coal.iloc[i-21])): continue
        m1=(coal.iloc[i]/coal.iloc[i-21]-1)*100; c=1.0 if t=='JSW' else 2.7; r=(a.iloc[i+21]/a.iloc[i]-1)*100-c
        rows.append(dict(d=idx[i],m1=m1,r=r,x=r-bench(i,i+21),sh=-(a.iloc[i+21]/a.iloc[i]-1)*100-0.96))
    g=pd.DataFrame(rows); y=g.d.dt.year
    for lab,m in [('coal 1m > +10%',g.m1>10),('coal 1m > 0',g.m1>0),('coal 1m <= 0',g.m1<=0),('coal 1m < -10%',g.m1<-10)]:
        s=g[m]; print(f"  {t} {lab:15s} n={len(s):3d} long net {s.r.mean():+5.2f} vsETF {s.x.mean():+5.2f} beats {100*(s.x>0).mean():3.0f}% t {s.x.mean()/s.x.std()*np.sqrt(len(s)):4.1f} | short net {s.sh.mean():+5.2f} | <2020 {s.x[y<2020].mean():+5.2f} 2020+ {s.x[y>=2020].mean():+5.2f}")
    print(f"  {t} corr(coal 1m, next month vs ETF) {g.m1.corr(g.x):+.3f} (n {len(g)})")
