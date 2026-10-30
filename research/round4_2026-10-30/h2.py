from lib import *
F=AD/CL
ev=[]
for t in TICK:
    if t not in LIQ: continue
    f=F[t].dropna(); y=1-f.shift(1)/f
    for d,v in y[(y>0.01)&(y<0.3)].items(): ev.append((t,idx.get_loc(d),v*100))
print("dividend events (liquid):",len(ev))
for lo,hi,lab in ((1,3,'1-3%'),(3,5,'3-5%'),(5,30,'>=5%'),(3,30,'>=3%')):
    E=[e for e in ev if lo<=e[2]<hi]
    for H in (21,):
        run=[trade(t,i-1-H,i-1) for t,i,v in E if i-1-H>=0]   # buy 21 before ex, sell cum-date close (no dividend received)
        post=[trade(t,i,i+H) for t,i,v in E if i+H<len(idx)]  # buy at ex-date close
        post5=[trade(t,i,i+5) for t,i,v in E if i+5<len(idx)]
        sh=[trade(t,i,i+H,short=True) for t,i,v in E if i+H<len(idx)]
        summ(run,f"yield {lab}: run-up 21 sessions before ex (sell cum)")
        df=summ(post,f"yield {lab}: buy ex-date close, hold 21")
        summ(post5,f"yield {lab}: buy ex-date close, hold 5")
        summ(sh,f"yield {lab}: XTB short ex-date close, 21")
pl=placebo(pd.DataFrame([x for x in post if x]),21); summ(pl.to_dict('records'),"placebo random 21d same stocks")
