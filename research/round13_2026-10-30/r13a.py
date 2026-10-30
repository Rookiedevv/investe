# Round 13a: re-audit of the live BANK READ-THROUGH rule vs the WIG20 TR ETF, on the full 2021-26 bank calendar (round 12 r12e.py list).
# Rule (claude/bank research): early reporter's results-day move minus the late reporters' average same-day move >= +1.5 pp -> buy the late
# reporters at the close of the reaction day; exit on the first day the stock falls more than 1.5x its normal daily move, max 20 sessions.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30')); sys.path.insert(0,os.path.join(H,'..','round12_2026-10-30'))
from lib import *
from r12e_cal import B
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1): return (ETF.iloc[i1]/ETF.iloc[i0]-1)*100-0.78
REL={t:(AD[t].pct_change()-W.pct_change())*100 for t in B if t in AD}
SD={t:AD[t].pct_change().rolling(60).std().shift(1)*100 for t in REL}
F=[]
for t,s in B.items():
    if t not in AD: continue
    for x in s.split():
        tm='a' if x.endswith('a') else ('d' if x.endswith('d') else 'b'); x=x.rstrip('ad'); d=pd.Timestamp('20'+x[:2]+'-'+x[2:4]+'-'+x[4:])
        i=idx.searchsorted(d)
        if i<len(idx) and idx[i]==d: F.append(dict(t=t,k=i+1 if tm=='a' else i))
F=pd.DataFrame(F).sort_values('k').reset_index(drop=True)
# seasons by calendar: Q4 prelims (Jan 15-Feb 15), annual reports (Feb 16-Mar), Q1 (Apr-May), H1 (Jul-Aug), Q3 (Oct-Nov); first filing per bank per season
def season(d):
    m,dd=d.month,d.day
    if (m==1 and dd>=15) or m in (2,3): return f"{d.year}-Q4"   # Q4 prelims and annual reports are one season (first Q4 news per bank)
    if m in (4,5): return f"{d.year}-Q1"
    if m in (7,8): return f"{d.year}-H1"
    if m in (10,11): return f"{d.year}-Q3"
    return None
F['c']=[season(idx[k]) for k in F.k]; F=F.dropna(subset=['c']); F=F.drop_duplicates(['c','t'],keep='first')
rows=[]
for c,g in F.groupby('c'):
    g=g.sort_values('k'); first=g.iloc[0]; k=first.k
    later=g[g.k>k+1]                                   # banks reporting at least 2 sessions later
    if len(later)<2: continue
    re1=REL[first.t].iloc[k]; others=np.nanmean([REL[t].iloc[k] for t in later.t]); S=re1-others
    for _,x in later.iterrows():
        t=x.t; a=AD[t]; i0=k; cap=min(x.k,k+20)        # hold to own report day, max 20
        # trailing exit: first day after entry with a fall > 1.5 sd (own daily move)
        j=i0+1; ex=None
        while j<=cap:
            if (a.iloc[j]/a.iloc[j-1]-1)*100 < -1.5*SD[t].iloc[j]: ex=j; break
            j+=1
        ex = ex if ex is not None else cap
        def ret(i1): r=(a.iloc[i1]/a.iloc[i0]-1)*100-1.0; return r, r-bench(i0,i1)
        r1,x1=ret(cap); r2,x2=ret(ex); r3,x3=ret(min(i0+20,len(idx)-1))
        rows.append(dict(d=idx[k],first=first.t,t=t,S=S,re1=re1,r_rep=r1,x_rep=x1,n_rep=cap-i0,r_stop=r2,x_stop=x2,n_stop=ex-i0,r_20=r3,x_20=x3))
D=pd.DataFrame(rows); print('quarters:',D.d.nunique(),'late-reporter trades:',len(D))
def rep(g,lab):
    if len(g)<4: print(f"{lab:40s} n={len(g)}"); return
    out=[f"{lab:40s} n={len(g):3d}"]
    for s in ('rep','stop','20'):
        x=g['x_'+s]; out.append(f"| {s}: net {g['r_'+s].mean():+5.2f} vsETF {x.mean():+5.2f} beats {100*(x>0).mean():3.0f}% t {x.mean()/x.std()*np.sqrt(len(x)):4.1f}")
    print(' '.join(out))
rep(D,'all quarters'); rep(D[D.S>=1.5],'signal S >= +1.5 (BUY)'); rep(D[D.S>=1.0],'S >= +1.0'); rep(D[D.S>=2.5],'S >= +2.5'); rep(D[D.S<=-1.5],'S <= -1.5 (stay out)'); rep(D[D.S.abs()<1.5],'|S| < 1.5')
rep(D[(D.S>=1.5)&(D.t.isin(['MBK','ING','PEO','PKO']))],'S>=1.5, tilt names MBK ING PEO PKO')
print('\nper-quarter signal and average late-reporter result (hold to report):')
q=D.groupby('d').agg(first=('first','first'),S=('S','first'),n=('t','count'),x_rep=('x_rep','mean'),x_stop=('x_stop','mean')).round(2); print(q.to_string())
print('\ncorr(S, late reporters vs ETF):',round(D.S.corr(D.x_rep),2))
