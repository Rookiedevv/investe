"""Round 36: test fundamental factors monthly on liquid GPW stocks (point in time)."""
import sys, pickle
from fac36 import *
import fund36 as F
START = sys.argv[1] if len(sys.argv) > 1 else "2011-01-01"; MINN = int(sys.argv[2]) if len(sys.argv) > 2 else 15
ME2 = [i for i in month_ends(START)]
import fac36; fac36.ME = ME2
SN = {}
for i in ME2: SN[i] = F.snapshot(i)
pickle.dump(SN, open('snap.pkl', 'wb'))
cols = F.QF + F.PF
PAN = {c: pd.DataFrame({idx[i]: SN[i][c].astype(float) for i in ME2 if len(SN[i])}).T for c in cols}
PAN['div_yield'] = F.DY.loc[[idx[i] for i in ME2]]
def zs(df):
    r = df.rank(axis=1, pct=True); return r
def pf(c): return lambda i: PAN[c].loc[idx[i]] if idx[i] in PAN[c].index else pd.Series(dtype=float)
def combo(cs, need=2):
    z = [zs(PAN[c]) for c in cs]; allc = sorted(set().union(*[x.columns for x in z])); z = [x.reindex(columns=allc) for x in z]
    cnt = sum(x.notna().astype(int) for x in z); tot = sum(x.fillna(0) for x in z)
    return (tot / cnt).where(cnt >= need)
PAN['value_combo'] = combo(('ep', 'bp', 'cfp', 'div_yield'))
PAN['quality_combo'] = combo(('roe', 'low_accruals', 'fscore', 'low_issuance'))
PAN['growth_combo'] = combo(('d_ni', 'd_rev', 'sue', 'd_margin'))
pickle.dump(PAN, open('pan.pkl', 'wb'))
if __name__ == '__main__':
    print('coverage (tickers with a fresh report) at a few dates:', {str(idx[i].date()): len(SN[i]) for i in ME2[::24]})
    RES = {}
    for c in PAN: RES[c] = evaluate(pf(c), c, minn=MINN)
    pickle.dump(RES, open('fund_res.pkl', 'wb'))
