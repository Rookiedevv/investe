"""Round 36: monthly cross-sectional factor tests on liquid GPW stocks."""
from lib36 import *
MINT = 2e6
ME = month_ends('2011-01-01')

def evaluate(f, lab, q=0.2, k=5, minn=15, mint=MINT, maxt=None, lag=0, hold_months=1, start=None, end=None, univ=None, quiet=False, sectors=None):
    """f(i) -> Series (higher = better). Monthly: rank liquid universe at month-end close, hold to next month-end."""
    rows = []
    for a in range(len(ME) - hold_months):
        i, j = ME[a], ME[a + hold_months]
        if start and idx[i] < pd.Timestamp(start): continue
        if end and idx[i] > pd.Timestamp(end): continue
        tv = TURN.iloc[i]
        U = tv[(tv >= mint) & ((tv < maxt) if maxt else True)].index
        if univ is not None: U = [t for t in U if t in univ]
        s = f(i).reindex(U).replace([np.inf, -np.inf], np.nan).dropna()
        g = fwd(i + lag, j).reindex(s.index).dropna(); s = s.reindex(g.index)
        if len(s) < minn: continue
        net = g - cost_s(i).reindex(g.index)
        w = wig(i + lag, j) - ETF_COST
        n5 = max(3, int(round(len(s) * q)))
        top = s.nlargest(n5).index; bot = s.nsmallest(n5).index; top5 = s.nlargest(k).index
        ic = s.rank().corr(g.rank())
        rows.append(dict(d=idx[i], n=len(s), top=net[top].mean(), bot=net[bot].mean(), univ=net.mean(), wig=w, top5=net[top5].mean(), ic=ic,
                         top5beat=(net[top5] > w).mean(), names=' '.join(top5)))
    D = pd.DataFrame(rows)
    if D.empty: return D
    D['xw'] = D.top - D.wig; D['xu'] = D.top - D.univ; D['bu'] = D.bot - D.univ; D['x5w'] = D.top5 - D.wig; D['x5u'] = D.top5 - D.univ
    if not quiet: line(D, lab)
    return D

def line(D, lab):
    h = len(D) // 2; a, b = D.iloc[:h], D.iloc[h:]
    print(f"{lab:26s} m={len(D):3d} n~{D.n.mean():3.0f} | top-univ {D.xu.mean():+5.2f} t{tstat(D.xu):5.1f} ({a.xu.mean():+4.1f}/{b.xu.mean():+4.1f}) bot-univ {D.bu.mean():+5.2f} | top-WIG {D.xw.mean():+5.2f} t{tstat(D.xw):4.1f} win{100*(D.xw>0).mean():3.0f}% | top5-WIG {D.x5w.mean():+5.2f} win{100*(D.x5w>0).mean():3.0f}% ({a.x5w.mean():+4.1f}/{b.x5w.mean():+4.1f}) top5-univ {D.x5u.mean():+5.2f} t{tstat(D.x5u):4.1f} | IC {D.ic.mean():+.3f} t{tstat(D.ic):4.1f}")

# ---------- price factors
LR = np.log(AD).diff()
def mom(i, a, b): return AD.iloc[i - b] / AD.iloc[i - a] - 1
def sd(i, n): return RET.iloc[i - n + 1:i + 1].std(min_count=int(n * .7)) if False else RET.iloc[i - n + 1:i + 1].apply(lambda c: c.std() if c.notna().sum() >= n * .7 else np.nan)
def beta_ivol(i, n=250):
    X = RET.iloc[i - n + 1:i + 1]; mk = WRET.iloc[i - n + 1:i + 1]
    ok = X.notna().sum() >= n * .7
    cov = X.apply(lambda c: c.cov(mk)); b = cov / mk.var()
    res = X.sub(mk, axis=0).mul(1)  # placeholder
    iv = (X - np.outer(mk.values, b.values)).std()
    return b.where(ok), iv.where(ok)
def resmom(i):
    X = RET.iloc[i - 252:i - 20]; mk = WRET.iloc[i - 252:i - 20]
    ok = X.notna().sum() >= 180
    b = X.apply(lambda c: c.cov(mk)) / mk.var(); e = X - np.outer(mk.values, b.values)
    return (e.sum() / (e.std() * np.sqrt(len(e)))).where(ok)
def consist(i):
    m = pd.concat([AD.iloc[i - 21 * (k + 1)] and None for k in []]) if False else None
    v = [(AD.iloc[i - 21 * k] / AD.iloc[i - 21 * (k + 1)] - 1) for k in range(1, 12)]
    v = pd.concat(v, axis=1); return (v > 0).sum(axis=1).where(v.notna().sum(axis=1) >= 10) / 11
def amihud(i, n=60):
    x = (RET.abs() / (CL * VO).replace(0, np.nan)).iloc[i - n + 1:i + 1]
    return x.mean().where(x.notna().sum() >= n * .7) * 1e6
FACT = {
 'mom12_1': lambda i: mom(i, 252, 21),
 'mom6_1': lambda i: mom(i, 126, 21),
 'mom6': lambda i: mom(i, 126, 0),
 'mom3': lambda i: mom(i, 63, 0),
 'rev1 (1m losers)': lambda i: -mom(i, 21, 0),
 'rev5 (1w losers)': lambda i: -mom(i, 5, 0),
 'lowvol60': lambda i: -sd(i, 60),
 'lowvol250': lambda i: -sd(i, 250),
 'lowbeta250': lambda i: -beta_ivol(i)[0],
 'lowivol250': lambda i: -beta_ivol(i)[1],
 'lowmax21 (no lottery)': lambda i: -RET.iloc[i - 20:i + 1].max(),
 'near 52w high': lambda i: AD.iloc[i] / AD.iloc[i - 251:i + 1].max(),
 'above ma200': lambda i: AD.iloc[i] / AD.iloc[i - 199:i + 1].mean(),
 'residual mom': resmom,
 'consistency 12m': consist,
 'mom12_1/vol': lambda i: mom(i, 252, 21) / sd(i, 250),
 'illiquid (amihud)': amihud,
 'small turnover': lambda i: -TURN.iloc[i],
 'big turnover': lambda i: TURN.iloc[i],
 'volume surge 21/250': lambda i: (CL * VO).iloc[i - 20:i + 1].mean() / (CL * VO).iloc[i - 249:i + 1].mean(),
 'neg skew 250': lambda i: -RET.iloc[i - 249:i + 1].skew(),
 'range pos 21d': lambda i: (CL.iloc[i] - LO.iloc[i - 20:i + 1].min()) / (HI.iloc[i - 20:i + 1].max() - LO.iloc[i - 20:i + 1].min()),
}
if __name__ == '__main__':
    import sys
    start = sys.argv[1] if len(sys.argv) > 1 else None
    print('monthly rebalance at month-end close, liquid >= 2m zl/day, quintiles; net of per-stock costs; WIG net of ETF cost; (first half/second half)')
    RES = {}
    for k, f in FACT.items(): RES[k] = evaluate(f, k, start=start)
    pd.to_pickle(RES, 'price_res.pkl')
