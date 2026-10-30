# Round 20b: sector momentum / reversal on the official WIG sector indices (survivorship-free), monthly 2010-2025, vs WIG. Price indices (no TR) for all.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
M=pd.read_csv(os.path.join(H,'indices_monthly.csv'),parse_dates=['date'])
def monthly(sym):
    s=M[M.symbol==sym].set_index('date').close; s.index=s.index.to_period('M'); return s[~s.index.duplicated(keep='last')]
secs=['WIG-BANKI','WIG-BUDOW','WIG-INFO','WIG-SPOZYW','WIG-MEDIA','WIG-TELKOM','WIG-PALIWA','WIG-NRCHOM','WIG-CHEMIA','WIG-ENERG','WIG-GORNIC','WIG-ODZIEZ','WIG-MOTO','WIG-LEKI','WIG-GRY']
PX=pd.DataFrame({s:monthly(s) for s in secs})
wig=pd.read_csv(R+'/data/prices/WIG20.csv',parse_dates=['date']).set_index('date').close.dropna(); PX['WIG']=wig.groupby(wig.index.to_period('M')).last()  # WIG itself is not in the price files; WIG20 price index as benchmark
PX=PX[(PX.index>='2009-01')&(PX.index<='2025-12')]; Rt=PX.pct_change()
def run(score,lab,top=1,cost=0.0125,ascending=False,minhist=12):
    hold=set(); out=[]; sw=0
    for i in range(13,len(Rt)):
        P=PX.iloc[:i][secs]; avail=[s for s in secs if P[s].iloc[-minhist-1:].notna().all() and np.isfinite(Rt.iloc[i][s])]
        if len(avail)<6: continue
        sc=score(P[avail]).dropna().sort_values(ascending=ascending); pick=set(sc.index[:top])
        r=np.mean([Rt.iloc[i][p] for p in pick]); chg=len(pick-hold)/max(len(pick),1); r-=cost*chg; sw+=len(pick-hold); hold=pick
        out.append((Rt.index[i],r,Rt.iloc[i]['WIG']))
    d=pd.DataFrame(out,columns=['m','r','b']).set_index('m'); x=(d.r-d.b)*100; ann=lambda s:100*((1+s).prod()**(12/len(s))-1)
    print(f"{lab:40s} months={len(d):3d} | ann {ann(d.r):+5.1f}% vs WIG20 {ann(d.b):+5.1f}% | excess {x.mean():+5.2f} pp/m, beats WIG20 {100*(x>0).mean():3.0f}%, t {x.mean()/x.std()*np.sqrt(len(x)):4.1f} | 2010-17 {x[x.index<'2018'].mean():+5.2f} 2018-25 {x[x.index>='2018'].mean():+5.2f}")
mom=lambda n:(lambda P:(P.iloc[-1]/P.iloc[-1-n]-1))
print('sector momentum, hold top-k sectors one month (1.25% per switched sector = buying 2-3 stocks):')
for n in (1,3,6,12):
    for k in (1,3): run(mom(n),f'best {n}m, top {k}',top=k)
run(lambda P:(P.iloc[-2]/P.iloc[-13]-1),'12-1 momentum, top 3',top=3)
print('\nsector reversal:')
for n in (1,3,12):
    for k in (1,3): run(mom(n),f'worst {n}m, top {k}',top=k,ascending=True)
print('\nno-cost version (is there any signal at all?):')
for n in (3,6,12): run(mom(n),f'best {n}m top 3, no cost',top=3,cost=0); run(mom(n),f'worst {n}m top 3, no cost',top=3,cost=0,ascending=True)
