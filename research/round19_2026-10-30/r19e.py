# Round 19e: MSCI index reviews 2015-2026 (msci_changes.csv from MSCI's public lists): Polish names added to / deleted from the MSCI Poland
# Standard index (large passive flows) and the Small Cap index. Windows: announcement (evening) -> next session close -> effective-date close
# (the "run-up into the flow"), and effective close -> +21 sessions (reversal). Long at eMakler costs, short at XTB costs, vs the ETF.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
m=pd.read_csv(os.path.join(H,'msci_changes.csv'),parse_dates=['announce_date','effective_date'])
# net classification per ticker-review: ST add (from SC or new) = big inflow; ST del (to SC) = net outflow; pure SC add = small inflow; pure SC del = outflow
ev=[]
for (rev,t),g in m.groupby(['review','ticker']):
    acts=set(zip(g['index'],g.action))
    if ('ST','add') in acts: kind='ST_add'
    elif ('ST','del') in acts: kind='ST_del'
    elif ('SC','add') in acts: kind='SC_add'
    else: kind='SC_del'
    ev.append(dict(review=rev,t=t,kind=kind,ann=g.announce_date.iloc[0],eff=g.effective_date.iloc[0]))
E=pd.DataFrame(ev); print('events:',len(E),E.kind.value_counts().to_dict())
rows=[]
for _,e in E.iterrows():
    t=e.t
    if t not in AD: continue
    a=AD[t]; ia=idx.searchsorted(e.ann)+1; ie=idx.searchsorted(e.eff)
    if idx[min(ie,len(idx)-1)]!=e.eff: ie=idx.searchsorted(e.eff)  # nearest session
    if ie+21>=len(idx): continue
    def rr(i0,i1):
        p0,p1=a.iloc[i0],a.iloc[i1]
        return np.nan if not(np.isfinite(p0) and np.isfinite(p1)) else (p1/p0-1)*100
    c=1.0 if t in L1 else (1.5 if t in L2 else 2.5)
    run=rr(ia,ie); post=rr(ie,ie+21); d0=rr(ia-1,ia); pre=rr(ia-22,ia-1)
    rows.append(dict(t=t,kind=e.kind,ann=e.ann,n_run=ie-ia,day1=d0,pre=pre-((W.iloc[ia-1]/W.iloc[ia-22]-1)*100) if np.isfinite(pre) else np.nan,
                     run=run,run_x=run-c-bench(ia,ie) if np.isfinite(run) else np.nan,run_short=-run-0.96 if np.isfinite(run) else np.nan,
                     post=post,post_x=post-c-bench(ie,ie+21) if np.isfinite(post) else np.nan,post_short=-post-0.96 if np.isfinite(post) else np.nan,liq=t in LIQ))
D=pd.DataFrame(rows); print('with prices:',len(D)); D.round(2).to_csv(os.path.join(H,'r19e_events.csv'),index=False)
def rep(g,lab):
    if len(g)<4: print(f"{lab:40s} n={len(g)}"); return
    print(f"{lab:40s} n={len(g):2d} | day1 {g.day1.mean():+5.2f} | run (ann+1 -> eff) long vsETF {g.run_x.mean():+5.2f} beats {100*(g.run_x>0).mean():3.0f}% short net {g.run_short.mean():+5.2f} | post 21 long vsETF {g.post_x.mean():+5.2f} beats {100*(g.post_x>0).mean():3.0f}% short net {g.post_short.mean():+5.2f} win {100*(g.post_short>0).mean():3.0f}%")
for k in ('ST_add','ST_del','SC_add','SC_del'): rep(D[D.kind==k],k)
rep(D[D.kind.isin(['ST_add','SC_add'])],'any addition'); rep(D[D.kind.isin(['ST_del','SC_del'])],'any deletion')
rep(D[(D.kind=='ST_del')&D.liq],'ST_del liquid names'); rep(D[(D.kind=='ST_add')&D.liq],'ST_add liquid names')
print('\nper event:'); print(D[['t','kind','ann','day1','run_x','post_x']].round(1).sort_values('ann').to_string(index=False))
