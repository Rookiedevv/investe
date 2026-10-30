from lib import *
from cal import C
for H in (5,10,21):
    rows=[]
    for t,s in C.items():
        if t not in AD or t not in LIQ: continue
        ds=sorted(pd.to_datetime(['20'+x for x in s.split()]))
        last=-999
        for d in ds:
            j=idx.searchsorted(d)  # release-day index (or next session)
            if j>=len(idx) or j-1-H<0: continue
            if j-last<H+5: last=j; continue   # previous release too close
            last=j
            rows.append(trade(t,j-1-H,j-1))
    df=summ(rows,f"pre-results run-up, hold {H} sessions, exit day before")
    pl=placebo(df,H); summ(pl.to_dict('records'),"   placebo same stocks/hold")
    if H==10:
        print(df.groupby('t').r.agg(['count','mean']).round(1).sort_values('mean').T.to_string())
