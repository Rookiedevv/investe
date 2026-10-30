# Round 12b: (1) index promotions/demotions as LONG/short trades vs the ETF bar; (2) ABB pricing-day buys re-run vs ETF; (3) turn-of-month in WIG20.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def bench(i0,i1):
    r=(ETF.iloc[i1]/ETF.iloc[i0]-1)*100 if idx[i0]>=pd.Timestamp('2019-02-01') else (W.iloc[i1]/W.iloc[i0]-1)*100+3.5*(i1-i0)/252
    return r-0.78
def cst(t): return 1.0 if t in L1 else (1.5 if t in L2 else 2.5)
rng=np.random.default_rng(7); RAND={}
def own_rand(t,hold=21,k=200):
    s=AD[t].dropna(); a=idx.get_loc(s.index[0]); b=idx.get_loc(s.index[-1])-hold; v=[]
    for _ in range(k):
        i=int(rng.integers(a,b)); v.append((AD[t].iloc[i+hold]/AD[t].iloc[i]-1)*100-cst(t)-bench(i,i+hold))
    return float(np.nanmean(v))
def rep(g,lab,col='x'):
    if len(g)<5: print(f"{lab:46s} n={len(g)}"); return
    y=g.d.dt.year; tt=g[col].mean()/g[col].std()*np.sqrt(len(g))
    print(f"{lab:46s} n={len(g):3d} net {g.r.mean():+5.2f}% | vs ETF {g[col].mean():+5.2f}pp med {g[col].median():+5.2f} t {tt:4.1f} beats {100*(g[col]>0).mean():3.0f}% | <2022 {g[col][y<2022].mean():+5.2f} 2022+ {g[col][y>=2022].mean():+5.2f} | excess {g[col].mean()-g.ctl.mean():+5.2f}")

# ---- 1. index changes (announce, effective, ticker, kind) from claude/index_changes.csv; P = promotion, D = demotion
IX = """180301 180319 CDR P|180301 180319 ACP D|180301 180319 NEU D|180530 180618 11B P|180906 180924 PLW P|181206 181227 TRK P|
190228 190318 DNP P|190228 190318 PLY P|190228 190318 ENG D|190228 190318 EUR D|190228 190318 VST P|190228 190318 PFL D|190228 190318 SNK D|
190606 190624 GNB P|190606 190624 WWL D|190905 190923 BNP P|190905 190923 TEN P|190905 190923 PXM D|190905 190923 TRK D|
200312 200317 ASE P|200305 200323 DOM P|200305 200323 NEU P|200305 200323 BRS D|200305 200323 CIG D|200604 200622 BML P|200604 200622 MRC P|200604 200622 FTE D|200604 200622 STP D|
200903 200921 DAT P|200903 200921 XTB P|200903 200921 GTN D|200903 200921 LWB D|201012 201015 ALE P|201012 201015 MBK D|201012 201015 VRG D|201124 201127 ACP P|201124 201127 CIG P|201201 201204 CRM P|
210304 210322 MRC P|210304 210322 ALR D|210304 210322 OAT P|210304 210322 PEP P|210304 210322 SLV P|210304 210322 STP P|210304 210322 BNP D|210304 210322 CIG D|210304 210322 CRM D|210304 210322 MAB D|
210602 210621 ASB P|210602 210621 MAB P|210602 210621 ECH D|210602 210621 GTC D|210902 210920 HUG P|210902 210920 STP D|211202 211220 PCO P|211202 211220 OAT D|
220303 220321 MBK P|220303 220321 PCO P|220303 220321 MRC D|220303 220321 TPE D|220303 220321 MBR P|220303 220321 AMC D|220602 220620 GPP P|220602 220620 LWB P|220602 220620 BML D|220602 220620 PLW D|
220801 220804 KTY P|220801 220804 BNP P|220901 220919 APR P|220901 220919 BMC P|220901 220919 STH P|220901 220919 ASE D|220901 220919 BNP D|220901 220919 CLN D|221102 221107 KRU P|221102 221107 ZEP P|
230302 230320 ALR P|230302 230320 CCC D|230302 230320 BML P|230302 230320 BNP P|230302 230320 DAT D|230302 230320 MRC D|230601 230619 CIG P|230601 230619 PEP D|230829 230901 ATC P|230905 230908 TIM P|
230831 230918 RVU P|230831 230918 BNP D|230831 230918 MAB D|230905 230918 GRX P|230929 231004 PXM P|240202 240207 COG P|240229 240318 BDX P|240229 240318 ACP D|240229 240318 ABE P|240229 240318 RBW P|240229 240318 SNT P|
240229 240318 BMC D|240229 240318 SVE D|240229 240318 ZEP D|240606 240624 BNP P|240606 240624 COG D|240704 240709 CBF P|240905 240923 MRB P|240905 240923 PXM D|241016 241021 CLN P|241025 241030 ZAB P|241028 241030 GRX D|
241205 241223 VOX P|241205 241223 CIG D|250306 250324 CCC P|250306 250324 ZAB P|250306 250324 CPS D|250306 250324 JSW D|250306 250324 LBW P|250306 250324 NWG P|250306 250324 PEP P|250306 250324 VRC P|
250306 250324 ATC D|250306 250324 BNP D|250306 250324 LWB D|250306 250324 RVU D|250605 250623 ASE P|250605 250623 BNP P|250605 250623 GEA D|250605 250623 SLV D|250904 250922 DIA P|250904 250922 CLN D|
260305 260323 TPE P|260305 260323 OPL D|260305 260323 CRI P|260305 260323 PXM P|260305 260323 11B D|260305 260323 HUG D|260603 260622 MUR P|260603 260622 EUR D"""
ev=[]
for x in IX.replace('\n','').split('|'):
    a,e,t,k=x.split(); ev.append((pd.Timestamp('20'+a[:2]+'-'+a[2:4]+'-'+a[4:]),pd.Timestamp('20'+e[:2]+'-'+e[2:4]+'-'+e[4:]),t,k))
print('index-change events:',len(ev),'with prices:',sum(t in AD for *_,t,_ in ev))
for lab,hold in (('announce close -> effective close',None),('announce close -> +21',21),('effective close -> +21',21)):
    rows=[]
    for a,e,t,k in ev:
        if t not in AD: continue
        i=idx.searchsorted(a); j=idx.searchsorted(e)
        if lab.startswith('effective'): i=j
        i1 = j if hold is None else i+hold
        if i1<=i or i1>=len(idx) or not (np.isfinite(AD[t].iloc[i]) and np.isfinite(AD[t].iloc[i1])): continue
        r=(AD[t].iloc[i1]/AD[t].iloc[i]-1)*100-cst(t)
        if t not in RAND: RAND[t]=own_rand(t)
        rows.append(dict(t=t,d=idx[i],k=k,r=r,x=r-bench(i,i1),ctl=RAND[t],n=i1-i))
    df=pd.DataFrame(rows); print('\n==',lab)
    for k,name in (('P','promotion (long)'),('D','demotion (long)')):
        g=df[df.k==k]; rep(g,name); rep(g[g.t.isin(L1|L2)],'   liquid only')
    # demotion as XTB short
    g=df[df.k=='D'].copy(); g['sh']=-(g.r+g.t.map(cst))-0.96; g['x']=g.sh; g['r']=g.sh; g['ctl']=0
    rep(g,'demotion as XTB short (abs net)')

# ---- 2. ABB pricing-day buys (claude/abb_buybacks.csv, launches 2020-26): buy at close of the first session after launch, hold 21
ABB="""200129 TEN|200427 CCC|200505 XTB|201022 TXT|201117 LPP|210112 TEN|210316 ALE|210601 BNP|220119 TEN|220413 APR|221018 PKN|230117 PCO|230417 CCC|230509 XTB|230612 ALE|230718 1AT|231005 ALE|
240205 XTB|240313 BNP|240416 ALE|240610 MRB|240711 RBW|240903 XTB|240910 EBP|241211 RBW|250317 CCC|250415 ALE|250519 XTB|250605 ALE|251112 ZAB|251201 ALE|251201 EBP|260127 PCO|260408 ALE|260615 ALE|260902 ALE|260902 XTB|261013 APR"""
rows=[]
for x in ABB.replace('\n','').split('|'):
    a,t=x.split(); d=pd.Timestamp('20'+a[:2]+'-'+a[2:4]+'-'+a[4:])
    if t not in AD: continue
    i=idx.searchsorted(d)+1                      # launches are after the close -> pricing day = next session; buy at its close
    if i+21>=len(idx): continue
    gap=(AD[t].iloc[i]/AD[t].iloc[i-1]-1)*100-(W.iloc[i]/W.iloc[i-1]-1)*100
    r=(AD[t].iloc[i+21]/AD[t].iloc[i]-1)*100-cst(t)
    if t not in RAND: RAND[t]=own_rand(t)
    rows.append(dict(t=t,d=idx[i],gap=gap,r=r,x=r-bench(i,i+21),ctl=RAND[t]))
df=pd.DataFrame(rows); print('\n== ABB: buy at pricing-day close, hold 21 (gap = pricing-day move vs WIG20)')
rep(df,'all launches'); rep(df[df.gap<=-3],'pricing-day gap <= -3%'); rep(df[~df.t.isin(['XTB','ALE'])],'excluding XTB and Allegro'); rep(df[df.t.isin(L1)],'L1 only')
print(df.round(1).to_string())  # noqa

# ---- 3. turn of month in WIG20 TR ETF: last 2 + first 3 sessions vs the rest
e=ETF.dropna(); e=e[e.index>='2019-02-01']; r=e.pct_change()*100
m=e.index.to_period('M'); pos=pd.Series(np.arange(len(e)),index=e.index).groupby(m).rank(); cnt=pd.Series(1,index=e.index).groupby(m).transform('sum')
tom=(pos<=3)|(pos>cnt-2)
print('\n== turn of month (ETF daily pct): TOM days mean %.3f (n=%d), other days %.3f (n=%d); annualised TOM-only %.1f%%, rest %.1f%%'%(r[tom].mean(),tom.sum(),r[~tom].mean(),(~tom).sum(),r[tom].mean()*tom.sum()/len(e)*252,r[~tom].mean()*(~tom).sum()/len(e)*252))
w=W.dropna(); w=w[w.index>='2011-01-01']; rw=w.pct_change()*100; m=w.index.to_period('M'); pos=pd.Series(np.arange(len(w)),index=w.index).groupby(m).rank(); cnt=pd.Series(1,index=w.index).groupby(m).transform('sum'); tom=(pos<=3)|(pos>cnt-2)
for y0,y1 in ((2011,2018),(2019,2026)):
    s=(rw.index.year>=y0)&(rw.index.year<=y1)
    print('   WIG20 %d-%d: TOM %.3f%%/day vs other %.3f%%/day'%(y0,y1,rw[s&tom].mean(),rw[s&~tom].mean()))
