from lib import *
exec(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'h4.py')).read().split('df=pd.DataFrame')[0].split('for v in')[0])
df=pd.DataFrame([x for x in ev(newhi&(VR>=2),21,gap=21) if x])
from scipy import stats
print("trimmed mean 5%%: %+.2f  | without trades >+40%%: %+.2f (n=%d)"%(stats.trim_mean(df.r,0.05),df[df.r<40].r.mean(),(df.r<40).sum()))
# monthly cross-sectional: 12-1 momentum and 1m reversal, liquid names, month-end rebalance
me=AD.resample('ME').last().index
me_i=[idx.searchsorted(d,side='right')-1 for d in me]; me_i=[i for i in me_i if i>260 and i+21<len(idx)]
liq=[t for t in TICK if t in LIQ]
res={k:[] for k in ('mom_top','mom_bot','rev_bot','rev_top','all')}
for i in me_i:
    a=AD[liq].iloc
    m12=a[i-21]/a[i-252]-1; m1=a[i]/a[i-21]-1
    ok=m12.dropna().index.intersection(m1.dropna().index)
    if len(ok)<12: continue
    q=len(ok)//5
    top=m12[ok].nlargest(q).index; bot=m12[ok].nsmallest(q).index
    r1b=m1[ok].nsmallest(q).index; r1t=m1[ok].nlargest(q).index
    for k,S,sh in (('mom_top',top,0),('mom_bot',bot,1),('rev_bot',r1b,0),('rev_top',r1t,1),('all',ok,0)):
        rr=[trade(t,i,i+21,bool(sh)) for t in S]; rr=[x['r'] for x in rr if x]
        res[k].append((idx[i],np.mean(rr)))
for k,v in res.items():
    s=pd.Series(dict(v)); a=s[s.index.year<2019].mean(); b=s[s.index.year>=2019].mean()
    print(f"{k:8s} (short if bot/top-rev) months {len(s)} avg/mo {s.mean():+.2f}% t {s.mean()/s.std()*np.sqrt(len(s)):.1f} win {100*(s>0).mean():.0f}%  <2019 {a:+.2f} 2019+ {b:+.2f}")
s=pd.Series(dict(res['mom_top'])); w=pd.Series({idx[i]:(W.iloc[i+21]/W.iloc[i]-1)*100 for i in me_i}).reindex(s.index)
x=s-w; print("mom_top minus WIG20: %+.2f pp/mo, t %.1f, beats W20 in %.0f%% of months; beats deposit 0.45%%: %.0f%%"%(x.mean(),x.mean()/x.std()*np.sqrt(len(x)),100*(x>0).mean(),100*(s>0.45).mean()))
print("worst month %.1f%%, best %.1f%%"%(s.min(),s.max()))
print(s.groupby(s.index.year).mean().round(1).to_string())
