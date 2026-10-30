# Round 12e: own-results drift for the 9 banks, 2021-26 (from claude/bank_events.csv). Banks file before the session by habit (PKO/PEO/ALR at night,
# others 07:00-08:50); exceptions flagged: 'a' = after the session, 'd' = during (Erste IR upload 09:30-11:51 — ESPI may have been earlier; treated as during).
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1): return (ETF.iloc[i1]/ETF.iloc[i0]-1)*100-0.78
B={
'ALR':"210428 210804 211027 220302 220427 220803 221104 230303 230426 230802 231026 240228 240425 240802 241024 250304 250425 250806 251029 260224 260424a 260804",
'EBP':"210428 210728 211027 220202 220223d 220426 220728 221026 230202 230222 230425 230726 231025 240131 240216d 240430 240724d 241029 250205 250225d 250430 250730 251029 260204d 260224 260430 260730",
'BHW':"210429 210820 211109 220217 220325 220509 220830 221114 230208 230322 230511 230830 231110 240214 240322 240509 240830 241113 250312 250508 250828 251113 260317 260507 260827",
'MBK':"210429 210803 211103 220208 220303a 220511 220803 221108 230209 230302a 230428 230802 231031 240208 240229 240510 240801 241031 250206 250228 250430 250731 251030 260210 260226 260430 260729",
'ING':"210506 210806 211104 220203 220311a 220506 220804 221103 230202 230317a 230511 230803 231102 240201 240308 240506 240807 241031 250206 250307a 250508 250731 251030 260210 260305a 260430 260730",
'PEO':"210506 210804 211104 220303 220428 220804 221103 230302 230427 230803 231108 240222 240430 240808 241107 250227 250430 250807 251030 260219 260430 260730",
'MIL':"210511 210726 211026 220201 220221 220426 220726 221024 230201 230215a 230428 230726 231027 240130 240228 240510 240726 241029 250131 250224 250512 250729 251024 260209 260227a 260428 260728",
'BNP':"210513 210812 211109 220303 220510 220811 221110 230301 230510 230810 231109 240301 240514 240813 241108 250313 250514 250812 251106 260211 260305 260507 260812",
'PKO':"210528 210812 211105 220224 220519 220818 221110 230310 230518 230824 231109 240307 240509 240822 241107 250313 250513 250813 251106 260312 260514 260813",
}
rows=[]
for t,s in B.items():
    if t not in AD: print('no prices',t); continue
    ev=[]
    for x in s.split():
        tm='a' if x.endswith('a') else ('d' if x.endswith('d') else 'b'); x=x.rstrip('ad')
        ev.append((pd.Timestamp('20'+x[:2]+'-'+x[2:4]+'-'+x[4:]),tm))
    ii=[idx.searchsorted(d) for d,_ in ev]
    for (d,tm),i in zip(ev,ii):
        if i>=len(idx) or idx[i]!=d: continue
        if any(0<i-j<=30 for j in ii): continue
        k=i+1 if tm=='a' else i
        if k+21>=len(idx): continue
        a=AD[t]; re=(a.iloc[k]/a.iloc[k-1]-1)*100-(W.iloc[k]/W.iloc[k-1]-1)*100
        r=(a.iloc[k+21]/a.iloc[k]-1)*100-1.0
        rows.append(dict(t=t,d=idx[k],tm=tm,re=re,r=r,x=r-bench(k,k+21)))
df=pd.DataFrame(rows); print('bank first-news filings:',len(df),df.tm.value_counts().to_dict())
def rep(g,lab):
    if len(g)<4: print(f"{lab:40s} n={len(g)}"); return
    y=g.d.dt.year; tt=g.x.mean()/g.x.std()*np.sqrt(len(g))
    print(f"{lab:40s} n={len(g):3d} net {g.r.mean():+5.2f}% | vs ETF {g.x.mean():+5.2f}pp med {g.x.median():+5.2f} t {tt:4.1f} beats {100*(g.x>0).mean():3.0f}% | 2021-22 {g.x[y<=2022].mean():+5.2f} 2023+ {g.x[y>=2023].mean():+5.2f}")
g=df[df.tm=='b']
for lo,hi in ((3,6),(2,6),(2,99),(3,99),(6,99),(1,3),(0,1),(-2,0),(-99,-2),(-99,-3)): rep(g[(g.re>=lo)&(g.re<hi)],f"pre-session, reaction {lo}..{hi}%")
rep(df[(df.tm!='b')],'after/during filings, any reaction')
print('\nper bank, reaction >= +2% pre-session'); print(g[g.re>=2].groupby('t').x.agg(['count','mean']).round(1).T.to_string())
print('\nall pre-session trades with reaction >= +3%:'); print(g[g.re>=3].sort_values('d').round(1).to_string())
print('\ncorrelation reaction vs next-21 vs ETF (pre-session):',round(g.re.corr(g.x),2))
