import os,sys; sys.path.insert(0,os.path.dirname(__file__))
exec(open(os.path.join(os.path.dirname(__file__),'r5.py')).read().split('print("== A.')[0])
MID=[t for t in LIQ if t not in 'PKO PEO PZU KGH PKN ALE DNP CDR LPP'.split()]
print("E detail: mid caps 31 Dec -> end Jan, per year (net, ETF, diff)")
for y in range(2014,2026):
    i2=idx.searchsorted(pd.Timestamp(f'{y}-12-31'),side='right')-1; i1=idx.searchsorted(pd.Timestamp(f'{y+1}-01-31'),side='right')-1
    n=sum(np.isfinite(AD[t].iloc[i2]) for t in MID)
    a=basket(MID,i2,i1); b=bench(i2,i1); print(y+1,f"n={n:2d}  mid {a:+6.2f}  ETF {b:+6.2f}  diff {a-b:+6.2f}")
# control: same mid-cap basket vs ETF in every other calendar month
rows={}
for i,j in pairs:
    mo=idx[j].month; rows.setdefault(mo,[]).append(basket(MID,i,j)-bench(i,j))
print("mid caps minus ETF by holding month:", {k:round(np.mean(v),2) for k,v in sorted(rows.items())})
print("  share of Januaries/other months mid>ETF:", round(np.mean(np.array(rows[1])>0),2), round(np.mean(np.concatenate([np.array(v) for k,v in rows.items() if k!=1])>0),2))
# smaller of the mid caps (L2) only and L1-mid
for lab,U in (("L2 small",sorted(L2)),("L1 mid",[t for t in MID if t in L1])):
    d=[]
    for y in range(2014,2026):
        i2=idx.searchsorted(pd.Timestamp(f'{y}-12-31'),side='right')-1; i1=idx.searchsorted(pd.Timestamp(f'{y+1}-01-31'),side='right')-1
        d.append(basket(U,i2,i1,1.5 if lab.startswith('L2') else 1.0)-bench(i2,i1))
    d=np.array(d); print(lab, f"avg {np.nanmean(d):+.2f}pp, beats ETF {np.mean(d>0)*100:.0f}% of years")
print("B detail: short WIG20 via FW20 for a month after WIG20 lags DAX/SPX")
for lab,S in (("DAX",DAX),("SPX",SPX)):
  for thr in (3,5):
    x=[]
    for i,j in pairs:
        gap=((W.iloc[i]/W.iloc[i-21])-(S.iloc[i]/S.iloc[i-21]))*100
        if gap<-thr: x.append((idx[i],-(W.iloc[j]/W.iloc[i]-1)*100-0.1))
    d=pd.DataFrame(x,columns=['d','r']); y=d.d.dt.year
    print(f"lag {lab}>{thr}pp: n={len(d)} short net {d.r.mean():+.2f}% med {d.r.median():+.2f} wins {100*(d.r>0).mean():.0f}% t {d.r.mean()/d.r.std()*np.sqrt(len(d)):.1f} <2019 {d.r[y<2019].mean():+.2f} 2019+ {d.r[y>=2019].mean():+.2f}")
allx=[-(W.iloc[j]/W.iloc[i]-1)*100-0.1 for i,j in pairs]; print(f"any month short WIG20: {np.mean(allx):+.2f}% wins {100*np.mean(np.array(allx)>0):.0f}%")
print("control, mid caps minus ETF by holding month (2015+):")
c={}
for i,j in pairs:
    if idx[j]<pd.Timestamp('2015-01-01'): continue
    v=basket(MID,i,j)-bench(i,j)
    if np.isfinite(v): c.setdefault(idx[j].month,[]).append(v)
for k in sorted(c): print(k, f"avg {np.mean(c[k]):+.2f} beats {100*np.mean(np.array(c[k])>0):.0f}% n={len(c[k])}")
