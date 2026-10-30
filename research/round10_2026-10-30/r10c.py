import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1): return (ETF.iloc[i1]/ETF.iloc[i0]-1)*100-0.78
P=pd.read_csv(os.path.join(H,'industry','pzpm_registrations.csv'))
P['total_units']=P.total_units.fillna(P.cars_units+P.vans_units)
P['yoy']=P.total_yoy_pct.fillna((P.total_units/P.total_units.shift(12)-1)*100)
P['acc']=P.yoy-P.yoy.shift(1).rolling(3).mean()
P['pub']=pd.to_datetime(P.pub_date).fillna(pd.to_datetime(P.month)+pd.offsets.MonthBegin(1)+pd.Timedelta(days=5))
rows=[]
for _,r in P.dropna(subset=['acc']).iterrows():
    i=idx.searchsorted(r.pub,side='right')        # next session after publication day (time unknown)
    if i+21>=len(idx): continue
    for t in ('CAR','APR'):
        x=(AD[t].iloc[i+21]/AD[t].iloc[i]-1)*100-1.0-bench(i,i+21)
        rows.append((t,idx[i],r.yoy,r.acc,x))
D=pd.DataFrame(rows,columns=['t','d','yoy','acc','x'])
for nm,m in (('all months',D.acc.notna()),('accel > +5pp',D.acc>5),('accel > +10pp',D.acc>10),('accel < -5pp',D.acc<-5),('accel < -10pp',D.acc<-10),('y/y > +10%',D.yoy>10),('y/y < 0',D.yoy<0)):
    g=D[m]; y=g.d.dt.year
    print(f"{nm:14s} n={len(g):3d} vs ETF {g.x.mean():+5.2f}pp med {g.x.median():+5.2f} t {g.x.mean()/g.x.std()*np.sqrt(len(g)):4.1f} beats {100*(g.x>0).mean():3.0f}% | <2023 {g.x[y<2023].mean():+5.2f} 2023+ {g.x[y>=2023].mean():+5.2f}")
print("corr(acc, next-month vs ETF):",round(D[['acc','x']].corr().iloc[0,1],2))
