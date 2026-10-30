# Round 19d: GPW IPOs 2015-2025 (ipos.csv): (a) post-IPO one-month drift (buy at the first close, hold 21); (b) 180-day lock-up expiry
# (short on XTB from session ~170 to ~200 after listing; long after the expiry dip); vs ETF. Uses whatever Yahoo history exists.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
ip=pd.read_csv(os.path.join(H,'ipos.csv'),parse_dates=['ipo_date'])
rows=[]
for _,x in ip.iterrows():
    t=x.ticker
    if t not in AD: print('  no prices:',t,x['name']); continue
    a=AD[t].dropna()
    if a.index[0]>x.ipo_date+pd.Timedelta(days=10): print(f'  history starts late: {t} {a.index[0].date()} (ipo {x.ipo_date.date()})'); continue
    i0=idx.searchsorted(x.ipo_date); 
    if idx[i0]!=x.ipo_date: i0=idx.searchsorted(a.index[0])
    def ret(j0,j1):
        if j1>=len(idx): return np.nan,np.nan
        p0,p1=AD[t].iloc[j0],AD[t].iloc[j1]
        if not(np.isfinite(p0) and np.isfinite(p1)): return np.nan,np.nan
        r=(p1/p0-1)*100; return r, r-bench(j0,j1)
    d1,_=ret(i0,i0+1); m1,m1x=ret(i0,i0+21); m3,m3x=ret(i0,i0+63); m6,m6x=ret(i0,i0+126)
    # lock-up: 180 calendar days ~ 125 sessions; window sessions 115..145 (short), and 145..166 (long after)
    lk_s,lk_sx=ret(i0+115,i0+145); post,postx=ret(i0+145,i0+166); pre,prex=ret(i0+95,i0+115)
    rows.append(dict(t=t,name=x['name'],ipo=x.ipo_date,day1=d1,m1=m1,m1x=m1x,m3x=m3x,m6x=m6x,pre=prex,lock=lk_s,lockx=lk_sx,post=postx))
D=pd.DataFrame(rows); print(f'\nIPOs with usable prices: {len(D)} of {len(ip)}')
def s(c,lab):
    v=D[c].dropna(); print(f"  {lab:52s} n={len(v):2d} mean {v.mean():+6.2f} median {v.median():+6.2f} positive {100*(v>0).mean():3.0f}% t {v.mean()/v.std()*np.sqrt(len(v)):4.1f}")
s('day1','first-day return (from first close to next close)'); s('m1x','month 1 vs ETF (buy first close, hold 21)'); s('m3x','months 1-3 vs ETF'); s('m6x','months 1-6 vs ETF')
s('pre','sessions 95-115 vs ETF (before lock-up window)'); s('lockx','sessions 115-145 vs ETF (180-day lock-up expiry window)'); s('post','sessions 145-166 vs ETF (after expiry)')
v=D.lock.dropna(); print(f"  XTB short over the lock-up window: net {(-v-0.96-0.7*30/252).mean():+.2f}%, win {100*((-v-1.04)>0).mean():.0f}% (n={len(v)})")
print('\nper IPO (lock-up window vs ETF):'); print(D[['t','ipo','m1x','lockx','post']].round(1).to_string(index=False))
