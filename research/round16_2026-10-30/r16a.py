# Round 16a: analyst-recommendation aggregates (from round 9 recs.csv): coverage initiations, consensus shifts (share of buys over 90 days), and
# "implied upside" (target / price) extremes -> 21-session returns vs the ETF, entered 5 sessions after the issue date (public availability).
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
def cst(t): return 1.0 if t in L1 else (1.5 if t in L2 else 2.5)
d=pd.read_csv(os.path.join(H,'..','round9_2026-10-30','recs.csv'),parse_dates=['issue_date']).dropna(subset=['issue_date'])
d=d[d.ticker.isin(AD.columns)].sort_values('issue_date').reset_index(drop=True)
buy={'kupuj','akumuluj','przeważaj','overweight','buy','accumulate'}; sell={'sprzedaj','redukuj','niedoważaj','sell','reduce','underweight'}
d['r']=d.rating.str.lower().str.strip(); d['isbuy']=d.r.isin(buy); d['issell']=d.r.isin(sell)
d['upside']=d.target/d.price_on_issue-1
# initiation = first recommendation by this broker for this ticker (ignore the first 180 days of the data per ticker to avoid left-censoring)
d['first_by_broker']=~d.duplicated(['ticker','broker'])
start=d.groupby('ticker').issue_date.transform('min'); d['init']=d.first_by_broker&(d.issue_date>start+pd.Timedelta(days=180))
LAG=5
def trade(t,date,hold=21):
    i=idx.searchsorted(date)+LAG
    if i+hold>=len(idx) or not(np.isfinite(AD[t].iloc[i]) and np.isfinite(AD[t].iloc[i+hold])): return None
    r=(AD[t].iloc[i+hold]/AD[t].iloc[i]-1)*100-cst(t); return r, r-bench(i,i+hold)
rows=[]
for k,x in d.iterrows():
    # consensus over the previous 90 days (including this rec): share of buys among recs for the ticker
    win=d[(d.ticker==x.ticker)&(d.issue_date<=x.issue_date)&(d.issue_date>x.issue_date-pd.Timedelta(days=90))]
    prev=d[(d.ticker==x.ticker)&(d.issue_date<=x.issue_date-pd.Timedelta(days=90))&(d.issue_date>x.issue_date-pd.Timedelta(days=180))]
    share=win.isbuy.mean(); share_prev=prev.isbuy.mean() if len(prev)>=2 else np.nan
    tr=trade(x.ticker,x.issue_date)
    if tr is None: continue
    rows.append(dict(t=x.ticker,d=x.issue_date,init=x.init,isbuy=x.isbuy,issell=x.issell,upside=x.upside,share=share,n90=len(win),dshare=share-share_prev if np.isfinite(share_prev) else np.nan,r=tr[0],x=tr[1]))
D=pd.DataFrame(rows); print('recs with trades:',len(D))
def rep(g,lab):
    if len(g)<8: print(f"{lab:52s} n={len(g)}"); return
    y=g.d.dt.year; print(f"{lab:52s} n={len(g):4d} net {g.r.mean():+5.2f} vsETF {g.x.mean():+5.2f} med {g.x.median():+5.2f} beats {100*(g.x>0).mean():3.0f}% t {g.x.mean()/g.x.std()*np.sqrt(len(g)):4.1f} | <2022 {g.x[y<2022].mean():+5.2f} 2022+ {g.x[y>=2022].mean():+5.2f}")
rep(D,'all recommendations (lag 5)')
rep(D[D.init],'coverage initiation (new broker on the name)'); rep(D[D.init&D.isbuy],'   initiation with a BUY'); rep(D[D.init&~D.isbuy&~D.issell],'   initiation with HOLD'); rep(D[D.init&D.issell],'   initiation with SELL')
rep(D[(D.n90>=3)&(D.share>=0.8)],'consensus: >=80% buys in last 90d (>=3 recs)'); rep(D[(D.n90>=3)&(D.share<=0.34)],'consensus: <=34% buys in last 90d')
rep(D[D.dshare>=0.4],'consensus improved by >=40 pp vs prior 90d'); rep(D[D.dshare<=-0.4],'consensus worsened by >=40 pp')
rep(D[D.upside>=0.4],'implied upside >= 40%'); rep(D[D.upside<=0],'target below price (upside <= 0)'); rep(D[D.upside<=-0.1],'target >=10% below price')
# dedupe by ticker-month to avoid clustering
D['m']=D.d.dt.to_period('M'); U=D.drop_duplicates(['t','m'])
print('\n-- de-duplicated to one per ticker-month'); rep(U[U.init&U.isbuy],'initiation with a BUY'); rep(U[U.upside<=-0.1],'target >=10% below price'); rep(U[(U.n90>=3)&(U.share<=0.34)],'<=34% buys in 90d')
g=U[U.upside<=-0.1].copy(); g['sh']=-(g.r+g.t.map(cst))-0.96; print('XTB short of names with target >=10% below price: abs net %+.2f win %.0f pct n=%d' % (g.sh.mean(),100*(g.sh>0).mean(),len(g)))
