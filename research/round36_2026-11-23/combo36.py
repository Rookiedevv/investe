import pickle, sys
from fac36 import *
import fac36
ME2 = month_ends('2011-01-01'); fac36.ME = ME2
PAN = pickle.load(open('pan.pkl', 'rb'))
dates = [idx[i] for i in ME2]
def price_panel(k): return pd.DataFrame({idx[i]: FACT[k](i) for i in ME2}).T
for k in ('mom12_1', 'mom6', 'mom12_1/vol', 'near 52w high', 'above ma200', 'rev1 (1m losers)', 'lowvol250', 'range pos 21d', 'residual mom'):
    PAN[k] = price_panel(k)
PAN['win1m'] = -PAN['rev1 (1m losers)']
def combo(cs, need=None):
    z = [PAN[c].rank(axis=1, pct=True) for c in cs]; allc = sorted(set().union(*[x.columns for x in z])); z = [x.reindex(index=dates, columns=allc) for x in z]
    cnt = sum(x.notna().astype(int) for x in z); tot = sum(x.fillna(0) for x in z)
    return (tot / cnt).where(cnt >= (need or len(cs)))
PAN['G+M (d_ni, sue, mom12/vol, 52wh)'] = combo(('d_ni', 'sue', 'mom12_1/vol', 'near 52w high'), 3)
PAN['G+M2 (growth_combo, mom6)'] = combo(('growth_combo', 'mom6'))
PAN['G+M3 (d_ni, mom12_1/vol)'] = combo(('d_ni', 'mom12_1/vol'))
PAN['G+M4 (sue, near 52w high)'] = combo(('sue', 'near 52w high'))
PAN['G+M+1m (d_ni, mom12/vol, win1m)'] = combo(('d_ni', 'mom12_1/vol', 'win1m'))
PAN['G+Q (growth_combo, roe)'] = combo(('growth_combo', 'roe'))
PAN['G+M+Q (d_ni, mom12/vol, roe)'] = combo(('d_ni', 'mom12_1/vol', 'roe'))
PAN['trend (mom12/vol, 52wh, ma200)'] = combo(('mom12_1/vol', 'near 52w high', 'above ma200'))
pickle.dump(PAN, open('pan2.pkl', 'wb'))
def pf(c): return lambda i: PAN[c].loc[idx[i]]
if __name__ == '__main__':
    RES = {}
    for c in ('d_ni', 'sue', 'growth_combo', 'mom12_1/vol', 'near 52w high', 'win1m', 'trend (mom12/vol, 52wh, ma200)', 'G+M (d_ni, sue, mom12/vol, 52wh)', 'G+M2 (growth_combo, mom6)', 'G+M3 (d_ni, mom12_1/vol)', 'G+M4 (sue, near 52w high)', 'G+M+1m (d_ni, mom12/vol, win1m)', 'G+Q (growth_combo, roe)', 'G+M+Q (d_ni, mom12/vol, roe)'):
        RES[c] = evaluate(pf(c), c[:26])
    pickle.dump(RES, open('combo_res.pkl', 'wb'))
