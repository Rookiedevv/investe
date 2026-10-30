# Round 17a: KNF net-short-position register (positions >=0.5% of share capital, 2012-2026, 2,300 rows scraped from rss.knf.gov.pl)
# -> do new short disclosures / increases / decreases, and aggregate short interest, predict the next 21 sessions vs the ETF?
# Entry: close of the session after the position date (KNF publishes the next business day). Long = eMakler cost; short = XTB CFD cost.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
def cst(t): return 1.0 if t in L1 else (1.5 if t in L2 else 2.5)
MAP={'LIVECHAT':'TXT','TEXT':'TXT','PKNORLEN':'PKN','DINOPL':'DNP','CDPROJEKT':'CDR','TSGAMES':'TEN','11BIT':'11B','PKOBP':'PKO','MBANK':'MBK','TAURONPE':'TPE',
 'CYFRPLSAT':'CPS','KETY':'KTY','KRUK':'KRU','PEPCO':'PCO','ALLEGRO':'ALE','ZABKA':'ZAB','EUROCASH':'EUR','ALIOR':'ALR','GRUPAAZOTY':'ATT','JSW':'JSW','KGHM':'KGH',
 'LPP':'LPP','PGE':'PGE','BUDIMEX':'BDX','RAINBOW':'RBW','PZU':'PZU','ASBIS':'ASB','ORANGEPL':'OPL','TRAKCJA':'TRK','BOGDANKA':'LWB','GPW':'GPW','MEDICALG':'MDG',
 'ENEA':'ENA','PEKAO':'PEO','MILLENNIUM':'MIL','ASSECOPOL':'ACP','HANDLOWY':'BHW','AUTOPARTN':'APR','XTB':'XTB','BENEFIT':'BFT','GTC':'GTC','ENERGA':'ENG'}
d=pd.read_csv(os.path.join(H,'knf','knf_hist.csv'),parse_dates=['pos_date'])
d['t']=d.issuer.map(MAP); d=d[d.t.isin(AD.columns)].sort_values(['holder','issuer','pos_date']).reset_index(drop=True)
print('rows with prices:',len(d),'issuers:',d.t.nunique())
# classify each row within holder-issuer: new episode (first row or gap > 120 days), increase, decrease, same
d['prev_pct']=d.groupby(['holder','issuer']).pct.shift(); d['prev_date']=d.groupby(['holder','issuer']).pos_date.shift()
gap=(d.pos_date-d.prev_date).dt.days
d['kind']=np.where(d.prev_pct.isna()|(gap>120),'new',np.where(d.pct>d.prev_pct,'up',np.where(d.pct<d.prev_pct,'down','same')))
d['big']=d.pct-d.prev_pct.fillna(0)
print(d.kind.value_counts().to_dict())
LAG=1; HOLD=21
def outcome(t,date,lag=LAG,hold=HOLD):
    i=idx.searchsorted(date)+lag
    if i+hold>=len(idx) or not(np.isfinite(AD[t].iloc[i]) and np.isfinite(AD[t].iloc[i+hold])): return None
    raw=(AD[t].iloc[i+hold]/AD[t].iloc[i]-1)*100
    return dict(raw=raw,long=raw-cst(t),x=raw-cst(t)-bench(i,i+hold),short=-raw-0.96,xshort=-raw-0.96-bench(i,i+hold),i=i)
rows=[]
for k,x in d.iterrows():
    o=outcome(x.t,x.pos_date)
    if o: rows.append(dict(t=x.t,d=x.pos_date,kind=x.kind,pct=x.pct,dp=x.big,holder=x.holder,**o))
D=pd.DataFrame(rows); D['y']=D.d.dt.year
def rep(g,lab):
    if len(g)<8: print(f"{lab:56s} n={len(g)}"); return
    print(f"{lab:56s} n={len(g):4d} long net {g.long.mean():+5.2f} vsETF {g.x.mean():+5.2f} beats {100*(g.x>0).mean():3.0f}% t {g.x.mean()/g.x.std()*np.sqrt(len(g)):4.1f} | XTB short net {g.short.mean():+5.2f} win {100*(g.short>0).mean():3.0f}% | <2022 {g.x[g.y<2022].mean():+5.2f} 2022+ {g.x[g.y>=2022].mean():+5.2f} (n {(g.y>=2022).sum()})")
print('\n== every register row (one holder-issuer-date), entry next session close, hold 21 ==')
rep(D,'all rows'); 
for k in ['new','up','down','same']: rep(D[D.kind==k],'  kind='+k)
rep(D[(D.kind=='new')&(D.pct>=0.7)],'  new position already >=0.7%')
rep(D[(D.kind=='up')&(D.dp>=0.2)],'  increase by >=0.2 pp'); rep(D[(D.kind=='down')&(D.dp<=-0.2)],'  decrease by >=0.2 pp (covering)')
# de-duplicate: one event per issuer-week
D['w']=D.d.dt.to_period('W'); U=D.sort_values('d').drop_duplicates(['t','w'])
print('\n== one row per issuer-week ==')
rep(U,'all'); 
for k in ['new','up','down']: rep(U[U.kind==k],'  kind='+k)
# liquidity split
rep(U[U.t.isin(L1)],'  L1 names only'); rep(U[(U.kind=='new')&U.t.isin(L1)],'  L1 new positions'); rep(U[(U.kind=='down')&U.t.isin(L1)],'  L1 decreases')
# per issuer
print('\n== per issuer (all rows, vsETF of long) ==')
for t,g in D.groupby('t'):
    if len(g)>=15: print(f"  {t:4s} n={len(g):3d} long vsETF {g.x.mean():+5.2f} beats {100*(g.x>0).mean():3.0f}%  new n={ (g.kind=='new').sum():3d} vsETF {g.x[g.kind=='new'].mean():+5.2f}  down n={(g.kind=='down').sum():3d} vsETF {g.x[g.kind=='down'].mean():+5.2f}")
# ---- aggregate short interest per issuer: sum over holders of latest disclosed pct; a holder is dropped 90 days after its last row (closure dates are not in the register)
print('\n== aggregate short interest (sum of open positions per issuer) ==')
days=idx[idx>='2013-01-01']
agg={}
for t,g in d.groupby('t'):
    s=pd.Series(0.0,index=days)
    for (h,_),gh in g.groupby(['holder','issuer']):
        gh=gh.sort_values('pos_date'); p=pd.Series(gh.pct.values,index=gh.pos_date.values)
        p=p[~p.index.duplicated(keep='last')].reindex(days,method='ffill')
        last=gh.pos_date.values; lastd=pd.Series(last,index=last).reindex(days,method='ffill')
        alive=(days-pd.to_datetime(lastd.values)).days<=90
        s=s+p.fillna(0).where(alive,0)
    agg[t]=s
A=pd.DataFrame(agg)
def ev_outcomes(mask,lab,lag=1,hold=21):
    rows=[]
    for t in A.columns:
        m=mask[t]; dates=m.index[m.fillna(False).values]
        last=None
        for dt in dates:
            if last is not None and (dt-last).days<30: continue
            last=dt; o=outcome(t,dt,lag,hold)
            if o: rows.append(dict(t=t,d=dt,**o))
    g=pd.DataFrame(rows)
    if len(g): g['y']=g.d.dt.year; rep(g,lab)
    else: print(lab,'n=0')
    return g
chg20=A-A.shift(20)
ev_outcomes(A.gt(A.rolling(126,min_periods=60).max().shift(1))&(A>=1.0),'aggregate short at 6-month high and >=1%')
ev_outcomes(chg20>=0.5,'aggregate short rose >=0.5 pp over 20 sessions')
ev_outcomes(chg20>=1.0,'aggregate short rose >=1.0 pp over 20 sessions')
ev_outcomes(chg20<=-0.5,'aggregate short fell >=0.5 pp over 20 sessions (covering)')
ev_outcomes(chg20<=-1.0,'aggregate short fell >=1.0 pp over 20 sessions')
ev_outcomes((A>=2.0)&(A.shift(1)<2.0),'aggregate short crosses above 2%')
ev_outcomes((A==0)&(A.shift(1)>0),'last short position disappears (all covered)')
# cross-check: 63-session horizon for the strongest signals
print('\n== hold 63 sessions ==')
ev_outcomes(chg20>=1.0,'rose >=1.0 pp /20s, hold 63',hold=63); ev_outcomes(chg20<=-1.0,'fell >=1.0 pp /20s, hold 63',hold=63)
A.round(2).to_csv(os.path.join(H,'knf','aggregate_short_interest.csv'))
D.round(3).to_csv(os.path.join(H,'r17a_events.csv'),index=False)
