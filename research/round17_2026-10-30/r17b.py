# Round 17b: SII Investor Sentiment Index (INI, weekly Thursday survey since May 2011; bull/neutral/bear shares) as a contrarian timing signal
# for the WIG20 TR ETF: forward 1/4/13-week returns after extremes, vs unconditional. Entry at the close of the Thursday the survey is published
# (survey closes Wednesday night, published Thursday morning) -> we use the next session after the survey date to be conservative.
import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'..','round9_2026-10-30'))
from lib import *
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
WIG=pd.read_csv(R+'/data/prices/WIG.csv',parse_dates=['date']).set_index('date')['close'].reindex(idx).ffill()
s=pd.read_csv(os.path.join(H,'sii_ini.csv'),parse_dates=['date']).set_index('date')
s['bb']=s.bull-s.bear; s['bb4']=s.bb.rolling(4).mean()
s['z']=(s.bb-s.bb.rolling(52,min_periods=26).mean())/s.bb.rolling(52,min_periods=26).std()
s['w26']=WIG.reindex(s.index,method='ffill').pct_change(26)*100
def fwd(date,weeks):
    i=idx.searchsorted(date)+1; j=i+5*weeks
    if j>=len(idx): return np.nan
    if idx[i]>=pd.Timestamp('2019-02-01'): return (ETF.iloc[j]/ETF.iloc[i]-1)*100-0.78
    return (W.iloc[j]/W.iloc[i]-1)*100+3.5*(5*weeks)/252-0.78
for wk in (1,4,13): s[f'f{wk}']=[fwd(d,wk) for d in s.index]
s.to_csv(os.path.join(H,'r17b_table.csv'))
print('weeks:',len(s),s.index.min().date(),s.index.max().date())
print('bull-bear: mean %.2f sd %.2f; pct bears>=50: %.1f; bulls>=60: %.1f' % (s.bb.mean(),s.bb.std(),100*(s.bear>=.5).mean(),100*(s.bull>=.6).mean()))
print('correlation of bull-bear with forward ETF return: 1w %.3f 4w %.3f 13w %.3f' % tuple(s.bb.corr(s[f'f{w}']) for w in (1,4,13)))
print('correlation of 4-week-avg bull-bear with forward: 1w %.3f 4w %.3f 13w %.3f' % tuple(s.bb4.corr(s[f'f{w}']) for w in (1,4,13)))
print('correlation of 52-week z-score with forward: 1w %.3f 4w %.3f 13w %.3f' % tuple(s.z.corr(s[f'f{w}']) for w in (1,4,13)))
def rep(m,lab,dedupe=True):
    g=s[m.fillna(False)]
    if dedupe:  # one signal per 4-week cluster
        keep=[]; last=None
        for d in g.index:
            if last is None or (d-last).days>=28: keep.append(d); last=d
        g=g.loc[keep]
    if len(g)<8: print(f"{lab:48s} n={len(g)}"); return
    out=f"{lab:48s} n={len(g):3d}"
    for w in (1,4,13):
        f=g[f'f{w}'].dropna(); u=s[f'f{w}'].dropna()
        out+=f" | {w:2d}w {f.mean():+5.2f} (uncond {u.mean():+5.2f}) win {100*(f>0).mean():3.0f}%"
    print(out)
print('\n== unconditional weekly rows (4-week = 20 sessions, net of ETF fee) ==')
rep(s.f1.notna(),'all weeks',dedupe=False)
print('\n== bearish extremes (contrarian buy) ==')
rep(s.bear>=0.45,'bears >= 45%'); rep(s.bear>=0.50,'bears >= 50%'); rep(s.bb<=-0.10,'bull-bear <= -10 pp'); rep(s.bb<=-0.20,'bull-bear <= -20 pp')
rep(s.bb4<=-0.05,'4-week avg bull-bear <= -5 pp'); rep(s.z<=-1.5,'z(bull-bear,52w) <= -1.5'); rep(s.z<=-2,'z <= -2')
rep((s.bb<=-0.10)&(s.w26<0),'bull-bear <= -10 pp AND WIG down over 26w'); rep((s.bb<=-0.10)&(s.w26>=0),'bull-bear <= -10 pp AND WIG up over 26w')
rep(s.bb<=s.bb.rolling(26,min_periods=20).min().shift(1),'bull-bear at a 26-week low')
print('\n== bullish extremes (stay out / short?) ==')
rep(s.bull>=0.60,'bulls >= 60%'); rep(s.bull>=0.65,'bulls >= 65%'); rep(s.bb>=0.30,'bull-bear >= 30 pp'); rep(s.bb>=0.40,'bull-bear >= 40 pp')
rep(s.bb4>=0.30,'4-week avg bull-bear >= 30 pp'); rep(s.z>=1.5,'z >= 1.5'); rep(s.z>=2,'z >= 2')
rep(s.bb>=s.bb.rolling(26,min_periods=20).max().shift(1),'bull-bear at a 26-week high')
print('\n== sentiment change (momentum of mood) ==')
dbb=s.bb.diff(4)
rep(dbb<=-0.25,'bull-bear fell >=25 pp in 4 weeks'); rep(dbb>=0.25,'bull-bear rose >=25 pp in 4 weeks')
rep((s.bb.diff()<=-0.20),'bull-bear fell >=20 pp in one week'); rep((s.bb.diff()>=0.20),'bull-bear rose >=20 pp in one week')
print('\n== quintiles of bull-bear (all weeks, 4-week forward) ==')
s['q']=pd.qcut(s.bb,5,labels=False)
for q,g in s.groupby('q'): print(f"  quintile {q} bb {g.bb.min():+.2f}..{g.bb.max():+.2f} n={len(g)} 1w {g.f1.mean():+5.2f} 4w {g.f4.mean():+5.2f} 13w {g.f13.mean():+5.2f} win4w {100*(g.f4>0).mean():3.0f}%")
print('\n== by era (4-week fwd, bottom vs top quintile) ==')
for lab,m in [('2011-2018',s.index<'2019'),('2019-2026',s.index>='2019')]:
    g=s[m]; print(f"  {lab}: q0 {g[g.q==0].f4.mean():+5.2f} (n {(g.q==0).sum()})  q4 {g[g.q==4].f4.mean():+5.2f} (n {(g.q==4).sum()})  all {g.f4.mean():+5.2f}")
