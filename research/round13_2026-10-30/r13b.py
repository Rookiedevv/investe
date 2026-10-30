# Round 13b: WIG20 ETF after big index down days (index mean reversion) and after big up days; hold 5/10/21. Benchmark = unconditional ETF hold of the same length.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
w=W.dropna(); r=w.pct_change()*100
def test(cond,lab):
    for hold in (5,10,21):
        rows=[];last=-99
        for i in range(260,len(w)-hold-1):
            if not cond(i) or i-last<hold: continue
            last=i; rows.append(((w.iloc[i+hold]/w.iloc[i]-1)*100-0.78, w.index[i].year))
        if len(rows)<5: print(lab,'n<5'); continue
        x=np.array([a for a,_ in rows]); y=np.array([b for _,b in rows]); base=(w.shift(-hold)/w-1).mean()*100-0.78
        print(f"{lab:36s} hold {hold:2d}: n={len(x):3d} net {x.mean():+5.2f}% (uncond {base:+5.2f}) win {100*(x>0).mean():3.0f}% t {x.mean()/x.std()*np.sqrt(len(x)):4.1f} | <2019 {x[y<2019].mean():+5.2f} 2019+ {x[y>=2019].mean():+5.2f}")
test(lambda i: r.iloc[i]<=-3,'WIG20 day <= -3%')
test(lambda i: r.iloc[i]<=-2,'WIG20 day <= -2%')
test(lambda i: (w.iloc[i]/w.iloc[i-5]-1)*100<=-5,'WIG20 5-day <= -5%')
test(lambda i: (w.iloc[i]/w.iloc[i-21]-1)*100<=-10,'WIG20 21-day <= -10%')
test(lambda i: r.iloc[i]>=3,'WIG20 day >= +3%')
test(lambda i: (w.iloc[i]/w.iloc[i-21]-1)*100>=10,'WIG20 21-day >= +10%')
