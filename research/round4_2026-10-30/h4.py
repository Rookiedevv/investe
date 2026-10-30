from lib import *
exec(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'h3.py')).read().split('base=')[0])
HI=AD.rolling(252,min_periods=240).max()
newhi=(AD>=HI)&(AD.shift(1)<HI.shift(1))
for v in (1,1.5,2,3):
  for H in (10,21,42):
    summ(ev(newhi&(VR>=v),H,gap=21),f"new 52w high, vol>={v}x, hold {H}")
df=pd.DataFrame([x for x in ev(newhi&(VR>=2),21,gap=21) if x])
# ticker-demeaned vs that ticker's random 21d
bl=pd.DataFrame([x for x in ev(EX.abs()<99,21,gap=21) if x]).groupby('t').r.mean()
df['adj']=df.r-df.t.map(bl)
print("excess over same-stock random 21d: %+.1f pp (t %.1f)"%(df.adj.mean(),df.adj.mean()/df.adj.std()*np.sqrt(len(df))))
print(df.groupby(df.d.dt.year).r.agg(['count','mean',lambda s:(s>0).mean()]).round(2).T.to_string())
print(df.groupby('t').r.agg(['count','mean']).round(1).sort_values('mean').T.to_string())
# cluster by month: average per calendar month then mean
m=df.groupby(df.d.dt.to_period('M')).r.mean(); print("month-clustered: months %d mean %+.1f t %.1f"%(len(m),m.mean(),m.mean()/m.std()*np.sqrt(len(m))))
print("L1 only:",df[df.t.isin(L1)].r.agg(['count','mean']).round(2).to_dict(), " worst",df.r.min().round(1)," best",df.r.max().round(1))
# when WIG20 itself is above/below its 200d avg
reg=(W>W.rolling(200).mean()); df['up']=df.d.map(reg)
print(df.groupby('up').r.agg(['count','mean']).round(2).to_string())
