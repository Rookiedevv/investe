import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
def cost(t): return 1.0 if t in L1 else (1.5 if t in L2 else 2.5)
def run(fn,stocks,lab,day=25):
    s=pd.read_csv(os.path.join(H,'industry',fn)); s['yoy']=(s.iloc[:,1]/s.iloc[:,1].shift(12)-1)*100
    s['acc']=s.yoy-s.yoy.shift(1).rolling(3).mean(); s['m']=pd.PeriodIndex(s.month,freq='M')
    out={}
    for _,r in s.dropna().iterrows():
        rel=(r.m+1).to_timestamp()+pd.Timedelta(days=day-1)      # conservative: GUS publishes ~18th-23rd of next month
        i=idx.searchsorted(rel)
        if i+21>=len(idx): continue
        for t in stocks:
            if t not in AD or not np.isfinite(AD[t].iloc[i]) or not np.isfinite(AD[t].iloc[i+21]): continue
            x=(AD[t].iloc[i+21]/AD[t].iloc[i]-1)*100-cost(t)-bench(i,i+21)
            out.setdefault('rows',[]).append((t,idx[i],r.yoy,r.acc,x))
    D=pd.DataFrame(out['rows'],columns=['t','d','yoy','acc','x'])
    print(f"== {lab}: {fn} -> {stocks} ==")
    for nm,m in (('all months',D.acc.notna()),('accel > +2pp',D.acc>2),('accel > +5pp',D.acc>5),('accel < -2pp',D.acc<-2),('accel < -5pp',D.acc<-5),('y/y > 0',D.yoy>0),('y/y < 0',D.yoy<0)):
        g=D[m]; y=g.d.dt.year
        if len(g)<4: continue
        print(f"  {nm:14s} n={len(g):3d} vs ETF {g.x.mean():+5.2f}pp med {g.x.median():+5.2f} t {g.x.mean()/g.x.std()*np.sqrt(len(g)):4.1f} beats {100*(g.x>0).mean():3.0f}% | <2021 {g.x[y<2021].mean():+5.2f} 2021+ {g.x[y>=2021].mean():+5.2f}")
run('eurostat_coal_mining_B05.csv',['JSW','LWB'],'Coal output -> coal miners')
run('eurostat_construction_F.csv',['BDX','PXM','MRB'],'Construction output -> builders')
run('eurostat_industry_BD.csv',['KGH','PKN','KTY'],'Industrial production -> industrials')
