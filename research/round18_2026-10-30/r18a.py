# Round 18a: WIG20 futures basis (FW20 front contract vs cash index) as a sentiment/positioning signal for the ETF; plus ETF seasonality (month of year,
# "sell in May") vs a ~0.35%/month deposit; plus overlap of the two "panic" signals (21-day drawdown >= 10%, SII z <= -1.5).
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
F=pd.read_csv(R+'/data/prices/FW20.csv',parse_dates=['date']).set_index('date')['close'].reindex(idx)
def fwd(i,hold):
    j=i+hold
    if j>=len(idx): return np.nan
    if idx[i]>=pd.Timestamp('2019-02-01'): return (ETF.iloc[j]/ETF.iloc[i]-1)*100-0.78
    return (W.iloc[j]/W.iloc[i]-1)*100+3.5*hold/252-0.78
w=W.copy(); basis=(F/w-1)*100
# de-trend the basis: deviation from its 60-session rolling median (removes the slow dividend/roll pattern), then a 250-session z-score
dev=basis-basis.rolling(60,min_periods=30).median(); z=(dev-dev.rolling(250,min_periods=120).mean())/dev.rolling(250,min_periods=120).std()
D=pd.DataFrame(dict(basis=basis,dev=dev,z=z)); D=D[D.index>='2005-01-01']
for h in (5,21,63): D[f'f{h}']=[fwd(idx.get_loc(d),h) for d in D.index]
D=D.dropna(subset=['z'])
print('days:',len(D),D.index.min().date(),D.index.max().date(),' basis mean %.2f sd %.2f'%(D.basis.mean(),D.basis.std()))
print('corr(z, fwd): 5d %.3f 21d %.3f 63d %.3f ; corr(dev, fwd21) %.3f'%(D.z.corr(D.f5),D.z.corr(D.f21),D.z.corr(D.f63),D.dev.corr(D.f21)))
def rep(m,lab,gap=21):
    g=D[m.fillna(False)]; keep=[];last=None
    for d in g.index:
        if last is None or (d-last).days>=gap: keep.append(d); last=d
    g=g.loc[keep]
    if len(g)<8: print(f"{lab:44s} n={len(g)}"); return
    out=f"{lab:44s} n={len(g):3d}"
    for h in (5,21,63):
        f=g[f'f{h}'].dropna(); u=D[f'f{h}'].dropna(); out+=f" | {h:2d}d {f.mean():+5.2f} (unc {u.mean():+5.2f}) win {100*(f>0).mean():3.0f}%"
    y=g.index.year; out+=f" | 21d <2019 {g.f21[y<2019].mean():+5.2f} 2019+ {g.f21[y>=2019].mean():+5.2f}"
    print(out)
print('\n== futures basis extremes (deviation from 60-session median, 250-session z) ==')
rep(D.z<=-2,'basis z <= -2 (futures unusually cheap)'); rep(D.z<=-1.5,'basis z <= -1.5'); rep(D.z>=2,'basis z >= +2 (futures unusually rich)'); rep(D.z>=1.5,'basis z >= +1.5')
rep(D.dev<=-0.5,'basis 0.5 pp below its 60d median'); rep(D.dev>=0.5,'basis 0.5 pp above its 60d median')
D['q']=pd.qcut(D.z,5,labels=False)
print('quintiles of basis z, 21d fwd:',' '.join(f"q{q} {g.f21.mean():+.2f}" for q,g in D.groupby('q')))
# ---- seasonality of the ETF benchmark: calendar-month returns (net of nothing; deposits ~0.35%/month in 2023-26, ~0.1-0.2% in 2015-21)
print('\n== ETF/WIG20 TR calendar-month returns 2005-2026 (gross, no fee) ==')
tr=pd.Series(index=idx,dtype=float)
for i in range(1,len(idx)):
    tr.iloc[i]=(ETF.iloc[i]/ETF.iloc[i-1]-1) if idx[i]>=pd.Timestamp('2019-02-01') and np.isfinite(ETF.iloc[i]) and np.isfinite(ETF.iloc[i-1]) else (W.iloc[i]/W.iloc[i-1]-1)+0.035/252
tr=tr[tr.index>='2005-01-01']; m=(1+tr).groupby([tr.index.year,tr.index.month]).prod()-1; m.index.names=['y','m']; mm=m.unstack()
print(' month: '+' '.join(f"{k:>6d}" for k in mm.columns)); print(' mean : '+' '.join(f"{100*v:+6.2f}" for v in mm.mean())); print(' win% : '+' '.join(f"{100*(mm[c]>0).mean():6.0f}" for c in mm.columns)); print(' n    : '+' '.join(f"{mm[c].notna().sum():6d}" for c in mm.columns))
nov_apr=mm[[11,12,1,2,3,4]]; may_oct=mm[[5,6,7,8,9,10]]
print(f' Nov-Apr mean/month {100*nov_apr.stack().mean():+.2f} (win {100*(nov_apr.stack()>0).mean():.0f}%)  May-Oct {100*may_oct.stack().mean():+.2f} (win {100*(may_oct.stack()>0).mean():.0f}%)')
print(f' per era: 2005-14 NovApr {100*nov_apr.loc[:2014].stack().mean():+.2f} MayOct {100*may_oct.loc[:2014].stack().mean():+.2f} | 2015-26 NovApr {100*nov_apr.loc[2015:].stack().mean():+.2f} MayOct {100*may_oct.loc[2015:].stack().mean():+.2f}')
# ---- overlap of panic signals
s=pd.read_csv(os.path.join(H,'..','round17_2026-10-30','r17b_table.csv'),parse_dates=['date']).set_index('date')
dd=(w/w.rolling(21).max()-1)*100
rows=[]
for d,row in s.iterrows():
    if not np.isfinite(row.z): continue
    i=idx.searchsorted(d)
    if i+21>=len(idx): continue
    rows.append(dict(d=d,sz=row.z,dd=dd.iloc[i],f21=fwd(i+1,21)))
P=pd.DataFrame(rows)
def rp(m,lab):
    g=P[m]; keep=[];last=None
    for d in g.d:
        if last is None or (d-last).days>=28: keep.append(d); last=d
    g=g[g.d.isin(keep)]
    print(f"{lab:44s} n={len(g):3d} 4w {g.f21.mean():+5.2f} win {100*(g.f21>0).mean():3.0f}%" if len(g) else lab+' n=0')
print('\n== panic signals on survey weeks (entry next session, 21 sessions) ==')
rp(P.sz<=-1.5,'SII z <= -1.5'); rp(P.dd<=-8,'WIG20 >= 8% below 21-day high'); rp((P.sz<=-1.5)&(P.dd<=-8),'both'); rp((P.sz<=-1.5)&(P.dd>-8),'SII only, no drawdown'); rp((P.sz>-1.5)&(P.dd<=-8),'drawdown only, SII not extreme'); rp((P.sz<=-1)|(P.dd<=-8),'either (z<=-1 or dd<=-8)')
