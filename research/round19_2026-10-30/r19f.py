# Round 19f: robustness of the MSCI Standard-addition reversal (short at the effective-date close on XTB, cover after N sessions).
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
m=pd.read_csv(os.path.join(H,'msci_changes.csv'),parse_dates=['announce_date','effective_date'])
adds=m[(m['index']=='ST')&(m.action=='add')&m.ticker.isin(AD.columns)]
print('Standard additions with prices:',len(adds),list(adds.ticker))
def path(t,i0,lag,hold):
    a=AD[t]; j0=i0+lag; j1=j0+hold
    if j1>=len(idx) or not(np.isfinite(a.iloc[j0]) and np.isfinite(a.iloc[j1])): return None
    r=(a.iloc[j1]/a.iloc[j0]-1)*100; wr=(W.iloc[j1]/W.iloc[j0]-1)*100
    return r, r-wr, -r-0.96-0.7*hold/252
print('\nentry lag (sessions after effective close) x hold: mean raw, vs WIG20, XTB short net, win%, t')
for lag in (0,1,3):
    for hold in (5,10,15,21,30,42,63):
        x=[path(r.ticker,idx.searchsorted(r.effective_date),lag,hold) for _,r in adds.iterrows()]; x=[v for v in x if v]
        raw=np.array([v[0] for v in x]); rel=np.array([v[1] for v in x]); sh=np.array([v[2] for v in x])
        print(f"  lag {lag} hold {hold:2d}: n={len(x):2d} raw {raw.mean():+6.2f} vsWIG {rel.mean():+6.2f} short net {sh.mean():+6.2f} win {100*(sh>0).mean():3.0f}% t {sh.mean()/sh.std()*np.sqrt(len(sh)):4.1f} median {np.median(sh):+5.2f}")
# placebo: same stocks, random 21-session shorts (200 draws per event) and the pre-announcement month
rng=np.random.default_rng(3); pl=[]
for _,r in adds.iterrows():
    s=AD[r.ticker].dropna(); ii=[idx.get_loc(d) for d in s.index]
    for _ in range(200):
        i0=int(rng.integers(ii[0]+1,ii[-1]-22)); v=path(r.ticker,i0,0,21)
        if v: pl.append(v[2])
print(f"\nplacebo random same-stock 21-session XTB shorts: net {np.mean(pl):+.2f}, win {100*(np.array(pl)>0).mean():.0f}%")
print('what happens before: announcement+1 -> effective (run) and the 21 sessions before announcement, vs WIG20')
for _,r in adds.iterrows():
    ia=idx.searchsorted(r.announce_date)+1; ie=idx.searchsorted(r.effective_date); a=AD[r.ticker]
    pre=(a.iloc[ia-1]/a.iloc[ia-22]-1)*100-(W.iloc[ia-1]/W.iloc[ia-22]-1)*100; run=(a.iloc[ie]/a.iloc[ia]-1)*100-(W.iloc[ie]/W.iloc[ia]-1)*100
    v=path(r.ticker,ie,0,21); v42=path(r.ticker,ie,0,42)
    print(f"  {r.ticker:4s} {r.review}: pre-ann month {pre:+6.1f} | run {run:+6.1f} ({ie-ia} sessions) | post 21 vsWIG {v[1] if v else float('nan'):+6.1f} | post 42 {v42[1] if v42 else float('nan'):+6.1f}")
# also the effective day itself (passive buying at the close): close-to-close on the effective date
d=[(AD[r.ticker].iloc[idx.searchsorted(r.effective_date)]/AD[r.ticker].iloc[idx.searchsorted(r.effective_date)-1]-1)*100-(W.iloc[idx.searchsorted(r.effective_date)]/W.iloc[idx.searchsorted(r.effective_date)-1]-1)*100 for _,r in adds.iterrows()]
print(f"\neffective-day return vs WIG20 (the flow day): mean {np.mean(d):+.2f}, positive {100*(np.array(d)>0).mean():.0f}%")
