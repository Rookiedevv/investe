# Round 12f: widen the Eurocash short lead with Jeronimo Martins / Biedronka releases (35 quarterly releases 2018-26), and test Dino/Zabka longs on the same days.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
B=pd.read_csv(os.path.join(H,'..','round8_2026-10-30','biedronka_lfl.csv'),parse_dates=['date'])
J=pd.read_csv(R+'/research/prices_foreign/JMT.LS.csv',parse_dates=['date']).set_index('date')['adj_close']
rows=[]
for k in range(1,len(B)):
    d=B.date[k]; tm=B.timing[k]; i=idx.searchsorted(d)
    if i>=len(idx) or idx[i]!=d: continue
    kk=i+1 if tm=='a' else i                      # Warsaw reaction day
    if kk+21>=len(idx): continue
    jd=J.index[J.index.searchsorted(d)]; jj=J.index.get_loc(jd); jm=(J.iloc[jj+(1 if tm=='a' else 0)]/J.iloc[jj-1+(1 if tm=='a' else 0)]-1)*100 if jj+1<len(J) else np.nan
    dl=B.lfl[k]-B.lfl[k-1]
    rec=dict(d=idx[kk],dlfl=dl,lfl=B.lfl[k],jm=jm)
    for t,c in (('EUR',2.5),('DNP',1.0),('ZAB',1.0),('PCO',1.0)):
        if t in AD and np.isfinite(AD[t].iloc[kk]) and np.isfinite(AD[t].iloc[kk+21]):
            r=(AD[t].iloc[kk+21]/AD[t].iloc[kk]-1)*100; rec[t+'_long']=r-c-bench(kk,kk+21); rec[t+'_short']=-r-(0.6+0.3+0.06)
            rec[t+'_re']=(AD[t].iloc[kk]/AD[t].iloc[kk-1]-1)*100-(W.iloc[kk]/W.iloc[kk-1]-1)*100
    rows.append(rec)
D=pd.DataFrame(rows); print('releases:',len(D))
def rep(s,lab):
    s=s.dropna()
    if len(s)<4: print(f"{lab:56s} n={len(s)}"); return
    print(f"{lab:56s} n={len(s):2d} mean {s.mean():+6.2f} med {s.median():+6.2f} win {100*(s>0).mean():3.0f}% t {s.mean()/s.std()*np.sqrt(len(s)):4.1f}")
print('\n-- Eurocash XTB short (abs net) after Biedronka releases')
rep(D.EUR_short,'all releases'); rep(D[D.dlfl>2].EUR_short,'LFL improved > 2pp'); rep(D[D.dlfl>0].EUR_short,'LFL improved > 0'); rep(D[D.dlfl<=0].EUR_short,'LFL worsened')
rep(D[D.jm<=-3].EUR_short,'JM share <= -3% on the day'); rep(D[D.jm>=3].EUR_short,'JM share >= +3%'); rep(D[D.DNP_re<=-3].EUR_short,'Dino reaction <= -3% that day')
print('\n-- Eurocash LONG vs ETF after Biedronka releases'); rep(D.EUR_long,'all'); rep(D[D.dlfl<=0].EUR_long,'LFL worsened'); rep(D[D.jm<=-3].EUR_long,'JM <= -3%')
print('\n-- Dino long vs ETF (control: live rule)'); rep(D[D.dlfl>2].DNP_long,'LFL improved > 2pp'); rep(D[D.jm>=3].DNP_long,'JM >= +3%'); rep(D[D.jm<=-3].DNP_long,'JM <= -3%'); rep(D[D.jm<=-3].DNP_short,'JM <= -3% -> Dino XTB short (abs)')
print('\n-- Zabka / Pepco'); rep(D[D.dlfl>2].ZAB_long,'Zabka long, LFL > 2pp'); rep(D.ZAB_long,'Zabka long all'); rep(D[D.dlfl>2].PCO_long,'Pepco long, LFL > 2pp')
print('\ncorr dLFL vs JM move %.2f; corr JM move vs Dino reaction %.2f; corr dLFL vs EUR 21d %.2f'%(D.dlfl.corr(D.jm),D.jm.corr(D.DNP_re),D.dlfl.corr(D.EUR_long)))
print(D.round(1).to_string())
