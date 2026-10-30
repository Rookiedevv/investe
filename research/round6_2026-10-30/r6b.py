import os,sys; sys.path.insert(0,os.path.dirname(__file__)); from r6 import *
D=run(1)
B=D[(D.t=='XTB')]
s=AD['XTB'].dropna(); ii=[idx.get_loc(d) for d in s.index]
base=[];rng=np.random.default_rng(2)
for _ in range(3000):
    j=int(rng.integers(ii[0],ii[-1]-21)); base.append(((AD['XTB'].iloc[j+21]/AD['XTB'].iloc[j]-1)*100-1.0)-bench(j,j+21))
base=np.array(base); base=base[np.isfinite(base)]; print(f"XTB random 21d vs ETF: {base.mean():+.2f} pp, beats ETF {100*(base>0).mean():.0f}%")
by=pd.Series(base)
for sign,lab in ((1,'peer UP'),(-1,'peer DOWN')):
    g=B[np.sign(B.v)==sign].copy(); g['x']=g.r-g.c-g.b
    g=g.sort_values('d').drop_duplicates('d')
    print(f"{lab}: n={len(g)} XTB vs ETF {g.x.mean():+.2f} pp, med {g.x.median():+.2f}, beats ETF {100*(g.x>0).mean():.0f}%, excess over XTB baseline {g.x.mean()-base.mean():+.2f}")
    print(g.groupby('peer').x.agg(['count','mean']).round(2).T.to_string())
    print(g.groupby(g.d.dt.year).x.agg(['count','mean']).round(1).T.to_string())
