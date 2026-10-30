# Round 19g: MSCI Standard-addition short entered at the OPEN of the session after the effective date (XTB, 09:00), covered at the close after k sessions.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
m=pd.read_csv(os.path.join(H,'msci_changes.csv'),parse_dates=['announce_date','effective_date'])
adds=m[(m['index']=='ST')&(m.action=='add')&m.ticker.isin(AD.columns)]
print('entry: open of effective+1 (XTB short, 0.96% + swap); exit: close of effective+k')
for k in (1,2,3,5,10,15,21):
    x=[]
    for _,r in adds.iterrows():
        p=P[r.ticker].reindex(idx); i=idx.searchsorted(r.effective_date)
        o1=p.open.iloc[i+1]; ck=p.close.iloc[i+k]; x.append(-(ck/o1-1)*100-0.96-0.7*k/252)
    x=np.array(x); print(f"  k={k:2d}: net {x.mean():+5.2f}% median {np.median(x):+5.2f} win {100*(x>0).mean():3.0f}% t {x.mean()/x.std()*np.sqrt(len(x)):4.1f} worst {x.min():+5.1f} best {x.max():+5.1f}")
print('per event, k=5:')
for _,r in adds.iterrows():
    p=P[r.ticker].reindex(idx); i=idx.searchsorted(r.effective_date); o1=p.open.iloc[i+1]
    print(f"  {r.ticker:4s} {r.review}: {-(p.close.iloc[i+5]/o1-1)*100-0.97:+6.2f}")
# same entry for Standard deletions (long at next open?) and small-cap additions for completeness
for lab,sel in [('ST deletions, LONG from next open',m[(m['index']=='ST')&(m.action=='del')]),('SC additions, SHORT from next open',m[(m['index']=='SC')&(m.action=='add')&~m.ticker.isin(adds.ticker)])]:
    sel=sel[sel.ticker.isin(AD.columns)]; x=[]
    for _,r in sel.iterrows():
        p=P[r.ticker].reindex(idx); i=idx.searchsorted(r.effective_date)
        if i+5>=len(idx) or not np.isfinite(p.open.iloc[i+1]): continue
        rr=(p.close.iloc[i+5]/p.open.iloc[i+1]-1)*100; x.append(rr-1.0 if 'LONG' in lab else -rr-0.97)
    x=np.array(x); print(f"{lab}: n={len(x)} net {x.mean():+.2f} win {100*(x>0).mean():.0f}%")
