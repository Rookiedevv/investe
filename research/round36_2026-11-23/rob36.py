import pickle
from fac36 import *
import fac36
from sectors import SEC
ME2 = month_ends('2011-01-01'); fac36.ME = ME2
PAN = pickle.load(open('pan2.pkl', 'rb'))
GM = 'G+M (d_ni, sue, mom12/vol, 52wh)'
def pf(c): return lambda i: PAN[c].loc[idx[i]] if idx[i] in PAN[c].index else pd.Series(dtype=float)
print('== base'); D = evaluate(pf(GM), 'G+M base')
D['y'] = D.d.dt.year
print(D.groupby('y').agg(m=('xw', 'size'), top=('top', 'mean'), univ=('univ', 'mean'), wig=('wig', 'mean'), top_wig=('xw', 'mean'), win=('xw', lambda v: 100 * (v > 0).mean()), top5_wig=('x5w', 'mean'), win5=('x5w', lambda v: 100 * (v > 0).mean()), bot_univ=('bu', 'mean')).round(1).to_string())
print('abs monthly net: top quintile %.2f%%, top5 %.2f%%, universe %.2f%%, WIG(net ETF cost) %.2f%% ; months top5 > 0.45%% (deposit): %.0f%% ; top5 beats both WIG and deposit: %.0f%%' % (D.top.mean(), D.top5.mean(), D.univ.mean(), D.wig.mean(), 100 * (D.top5 > .45).mean(), 100 * ((D.top5 > D.wig) & (D.top5 > .45)).mean()))
print('worst months top5-WIG:', D.nsmallest(5, 'x5w')[['d', 'x5w']].round(1).values.tolist(), ' best:', D.nlargest(5, 'x5w')[['d', 'x5w']].round(1).values.tolist())
print('median top5-WIG %.2f, median top-WIG %.2f ; share of individual top5 stock-months beating WIG %.0f%%' % (D.x5w.median(), D.xw.median(), 100 * D.top5beat.mean()))
print('thirds top5-WIG:', [round(D.x5w.iloc[a:b].mean(), 2) for a, b in ((0, 63), (63, 126), (126, 190))], 'top-univ:', [round(D.xu.iloc[a:b].mean(), 2) for a, b in ((0, 63), (63, 126), (126, 190))])
# name turnover of the top5 basket
ch = [len(set(a.split()) - set(b.split())) for a, b in zip(D.names.iloc[1:], D.names.iloc[:-1])]; print('avg new names per month in top5: %.1f of 5' % np.mean(ch))
print('== entry one session later'); evaluate(pf(GM), 'lag 1 session', lag=1)
print('== hold 2 / 3 months (overlapping)'); evaluate(pf(GM), 'hold 2m', hold_months=2); evaluate(pf(GM), 'hold 3m', hold_months=3)
print('== cohorts')
for lab, a, b in (('LARGE >=30m', 30e6, None), ('MID 10-30m', 10e6, 30e6), ('SMALL-LIQ 2-10m', 2e6, 10e6), ('>=10m', 10e6, None), ('>=5m', 5e6, None), ('>=1m', 1e6, None)):
    evaluate(pf(GM), lab, mint=a, maxt=b, minn=8, q=0.34 if (b or a >= 10e6) else 0.2, k=3 if (b or a >= 10e6) else 5)
nf = [t for t in TICK if SEC.get(t) not in ('banks', 'finance')]
evaluate(pf(GM), 'ex banks/finance', univ=set(nf))
evaluate(pf(GM), 'top 3', k=3); evaluate(pf(GM), 'top 8', k=8); evaluate(pf(GM), 'top 10', k=10)
print('== leave one component out / pairs')
dates = [idx[i] for i in ME2]
def combo(cs, need=None):
    z = [PAN[c].rank(axis=1, pct=True) for c in cs]; allc = sorted(set().union(*[x.columns for x in z])); z = [x.reindex(index=dates, columns=allc) for x in z]
    cnt = sum(x.notna().astype(int) for x in z); tot = sum(x.fillna(0) for x in z); return (tot / cnt).where(cnt >= (need or len(cs)))
base = ('d_ni', 'sue', 'mom12_1/vol', 'near 52w high')
for drop in base:
    cs = tuple(c for c in base if c != drop); PAN['x'] = combo(cs, 2); evaluate(pf('x'), 'without ' + drop)
for cs in (('d_ni', 'sue'), ('mom12_1/vol', 'near 52w high'), ('d_ni', 'mom12_1'), ('growth_combo', 'trend (mom12/vol, 52wh, ma200)'), ('d_ebit', 'mom6'), ('d_ni', 'sue', 'd_rev', 'mom12_1/vol', 'near 52w high', 'mom6')):
    PAN['x'] = combo(cs, max(2, len(cs) - 1)); evaluate(pf('x'), '+'.join(cs)[:26])
print('== quintile ladder (net - universe, pp/month)')
rows = []
for a in range(len(ME2) - 1):
    i, j = ME2[a], ME2[a + 1]; tv = TURN.iloc[i]; U = tv[tv >= 2e6].index
    s = PAN[GM].loc[idx[i]].reindex(U).dropna(); g = fwd(i, j).reindex(s.index).dropna(); s = s.reindex(g.index)
    if len(s) < 15: continue
    net = g - cost_s(i).reindex(g.index); qq = pd.qcut(s.rank(method='first'), 5, labels=False)
    rows.append((net.groupby(qq).mean() - net.mean()).values)
L = pd.DataFrame(rows); print('Q1(worst)..Q5(best):', L.mean().round(2).values, ' t:', [round(tstat(L[c]), 1) for c in L])
print('== placebo: shuffle the composite across stocks within each month (200 draws) -> distribution of top-univ t and top5-WIG mean')
rng = np.random.default_rng(1); T = []; M5 = []
base_panel = PAN[GM].copy()
for k in range(200):
    sh = base_panel.apply(lambda r_: pd.Series(rng.permutation(r_.values), index=r_.index) if False else r_, axis=1)
    def f(i, _rng=rng):
        s = base_panel.loc[idx[i]]; tv = TURN.iloc[i]; s = s[(tv >= 2e6).reindex(s.index).fillna(False)].dropna()
        return pd.Series(_rng.permutation(s.values), index=s.index)
    X = evaluate(f, 'p', quiet=True); T.append(tstat(X.xu)); M5.append(X.x5w.mean())
T = np.array(T); M5 = np.array(M5)
print('placebo top-univ t: mean %.2f sd %.2f max %.2f ; placebo top5-WIG mean %.2f sd %.2f max %.2f ; real: t %.1f, top5-WIG %.2f' % (T.mean(), T.std(), T.max(), M5.mean(), M5.std(), M5.max(), tstat(D.xu), D.x5w.mean()))
D.to_csv('gm_monthly.csv', index=False)
