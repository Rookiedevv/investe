"""Round 36: point-in-time fundamentals panel from research/fundamentals/*.csv (biznesradar)."""
from lib36 import *
FD = R + '/research/fundamentals/'
inc = pd.read_csv(FD + 'income_q.csv', low_memory=False); bal = pd.read_csv(FD + 'balance_q.csv', low_memory=False)
cf = pd.read_csv(FD + 'cashflow_q.csv', low_memory=False); mk = pd.read_csv(FD + 'market_q.csv', low_memory=False)
def col(d, *names):
    out = pd.Series(np.nan, index=d.index)
    for n in names:
        if n in d: out = out.fillna(pd.to_numeric(d[n], errors='coerce'))
    return out
def qnum(p): return p.str[:4].astype(int) * 4 + p.str[6:7].astype(int) - 1
Q = inc[['ticker', 'period', 'pub_date']].copy(); Q['q'] = qnum(Q.period)
Q['NI'] = col(inc, 'IncomeShareholderNetProfit', 'IncomeNetProfit')
Q['REV'] = col(inc, 'IncomeRevenues'); Q['BANKREV'] = col(inc, 'IncomeNetIntrestIncome') + col(inc, 'IncomeNetFeeExpense').fillna(0)
Q['FIN'] = Q.REV.isna() & Q.BANKREV.notna(); Q['REV'] = Q.REV.fillna(Q.BANKREV)
Q['EBIT'] = col(inc, 'IncomeEBIT', 'IncomeNetoperatingProfit', 'IncomeBeforTaxProfit'); Q['EBITDA'] = col(inc, 'IncomeEBITDA'); Q['GP'] = col(inc, 'IncomeGrossProfit')
b = bal.copy(); b['q'] = qnum(b.period)
b['EQ'] = col(bal, 'BalanceCapital', 'BalanceOwnCapital', 'BalanceTotalCapital'); b['TA'] = col(bal, 'BalanceTotalAssets'); b['CASH'] = col(bal, 'BalanceCash')
b['DEBT'] = sum(col(bal, c).fillna(0) for c in ('BalanceNoncurrentBorrowings', 'BalanceNoncurrentObligations', 'BalanceNoncurrentLeasing', 'BalanceCurrentBorrowings', 'BalanceCurrentObligations', 'BalanceCurrentLeasing'))
b['pub_b'] = b.pub_date
Q = Q.merge(b[['ticker', 'q', 'EQ', 'TA', 'CASH', 'DEBT', 'pub_b']], on=['ticker', 'q'], how='left')
c = cf.copy(); c['q'] = qnum(c.period); c['CFO'] = col(cf, 'CashflowOperatingCashflow'); c['CAPEX'] = col(cf, 'CashflowCapex'); c['DIVP'] = col(cf, 'CashflowDividend')
Q = Q.merge(c[['ticker', 'q', 'CFO', 'CAPEX', 'DIVP']], on=['ticker', 'q'], how='left')
m_ = mk.copy(); m_['q'] = qnum(m_.period); m_['SH'] = col(mk, 'ShareAmount'); m_['QUOTE'] = col(mk, 'Quote')
Q = Q.merge(m_[['ticker', 'q', 'SH', 'QUOTE']], on=['ticker', 'q'], how='left')
Q = Q.sort_values(['ticker', 'q']).reset_index(drop=True)
# availability date: publication date; fallback = quarter end + 75 days (Q4: + 120)
qend = pd.to_datetime((Q.q // 4).astype(str) + '-' + ((Q.q % 4 + 1) * 3).astype(str).str.zfill(2) + '-01') + pd.offsets.MonthEnd(0)
Q['qend'] = qend
pub = pd.to_datetime(Q.pub_date.fillna(Q.pub_b), errors='coerce')
Q['avail'] = pub.fillna(qend + pd.to_timedelta(np.where(Q.q % 4 == 3, 120, 75), unit='D'))
Q['pub_known'] = pub.notna()
g = Q.groupby('ticker')
def lagq(c, k):  # value k quarters earlier (only if that exact quarter exists)
    s = Q.set_index(['ticker', 'q'])[c]; ix = pd.MultiIndex.from_arrays([Q.ticker, Q.q - k]); return pd.Series(s.reindex(ix).values, index=Q.index)
def ttm(c): return sum(lagq(c, k) for k in range(4))
for c_ in ('NI', 'REV', 'EBIT', 'EBITDA', 'GP', 'CFO', 'CAPEX', 'DIVP'): Q[c_ + '4'] = ttm(c_)
EQa = (Q.EQ + lagq('EQ', 4)) / 2; EQa = EQa.fillna(Q.EQ)
Q['roe'] = (Q.NI4 / EQa).where(EQa > 0); Q['roa'] = Q.NI4 / Q.TA
Q['gpa'] = (Q.GP4 / Q.TA).where(~Q.FIN); Q['ebit_margin'] = (Q.EBIT4 / Q.REV4).where((Q.REV4 > 0) & ~Q.FIN)
Q['low_accruals'] = (-(Q.NI4 - Q.CFO4) / Q.TA).where(~Q.FIN)
Q['d_ni'] = ((Q.NI - lagq('NI', 4)) / lagq('EQ', 4)).where(lagq('EQ', 4) > 0)          # latest-quarter profit change y/y, scaled by equity
Q['d_ni4'] = ((Q.NI4 - lagq('NI4', 4)) / lagq('EQ', 4)).where(lagq('EQ', 4) > 0)       # TTM profit change y/y
Q['d_rev'] = (Q.REV / lagq('REV', 4) - 1).where(lagq('REV', 4) > 0)
Q['d_rev4'] = (Q.REV4 / lagq('REV4', 4) - 1).where(lagq('REV4', 4) > 0)
Q['d_ebit'] = ((Q.EBIT - lagq('EBIT', 4)) / lagq('TA', 4))
Q['d_margin'] = (Q.EBIT / Q.REV - lagq('EBIT', 4) / lagq('REV', 4)).where((Q.REV > 0) & (lagq('REV', 4) > 0) & ~Q.FIN)
Q['rev_accel'] = Q.d_rev - (lagq('d_rev', 1) + lagq('d_rev', 2) + lagq('d_rev', 3)) / 3
dn = Q.NI - lagq('NI', 4); Q['_dn'] = dn
sdn = pd.concat([lagq('_dn', k) for k in range(1, 9)], axis=1)
Q['sue'] = (dn / sdn.std(axis=1).where(sdn.notna().sum(axis=1) >= 6))
Q['low_issuance'] = -(Q.SH / lagq('SH', 4) - 1)
Q['low_asset_growth'] = -(Q.TA / lagq('TA', 4) - 1)
Q['low_leverage'] = (-(Q.DEBT - Q.CASH.fillna(0)) / Q.TA).where(~Q.FIN)
Q['d_roe'] = Q.roe - lagq('roe', 4)
# Piotroski-style score (non-financials get all 8 tests; financials only those defined)
fs = [(Q.NI4 > 0), (Q.CFO4 > 0), (Q.roa > lagq('roa', 4)), (Q.CFO4 > Q.NI4), ((Q.DEBT / Q.TA) < lagq('DEBT', 4) / lagq('TA', 4)), (Q.SH <= lagq('SH', 4) * 1.001),
      ((Q.GP4 / Q.REV4) > lagq('GP4', 4) / lagq('REV4', 4)), ((Q.REV4 / Q.TA) > lagq('REV4', 4) / lagq('TA', 4))]
Q['fscore'] = sum(f.astype(float) for f in fs).where(lagq('TA', 4).notna() & Q.NI4.notna())
QF = ['roe', 'roa', 'gpa', 'ebit_margin', 'low_accruals', 'd_ni', 'd_ni4', 'd_rev', 'd_rev4', 'd_ebit', 'd_margin', 'rev_accel', 'sue', 'low_issuance', 'low_asset_growth', 'low_leverage', 'd_roe', 'fscore']
# split guard: biznesradar share counts are as reported; Yahoo closes are split-adjusted. Scale shares where quote/close at quarter end disagree.
def _cl_at(t, d):
    if t not in CL: return np.nan
    s = CL[t].loc[:d].dropna(); return s.iloc[-1] if len(s) and (d - s.index[-1]).days < 10 else np.nan
Q['cl_qend'] = [_cl_at(t, d) for t, d in zip(Q.ticker, Q.qend)]
ratio = Q.QUOTE / Q.cl_qend
Q['SHadj'] = Q.SH * np.where((ratio > 1.4) | (ratio < 0.7), ratio, 1.0)
Q['SHadj'] = Q.SHadj.fillna(Q.SH)
BYT = {t: d.sort_values('avail') for t, d in Q.groupby('ticker')}

def snapshot(i, max_age=150):
    """latest published quarter per ticker as of the close of session i (published strictly before that day)"""
    D = idx[i]; rows = {}
    for t, d in BYT.items():
        x = d[d.avail < D]
        if not len(x): continue
        r_ = x.loc[x.q.idxmax()] if False else x.iloc[-1]
        r_ = x[x.q == x.q.max()].iloc[-1]
        if (D - r_.avail).days > max_age: continue
        rows[t] = r_
    S = pd.DataFrame(rows).T
    if S.empty: return S
    px = CL.iloc[i].reindex(S.index)
    mc = px * S.SHadj.astype(float) / 1000.0     # thousands PLN, same unit as statements
    S['mcap'] = mc
    S['ep'] = S.NI4.astype(float) / mc; S['bp'] = S.EQ.astype(float) / mc
    S['sp'] = (S.REV4.astype(float) / mc).where(~S.FIN.astype(bool)); S['cfp'] = (S.CFO4.astype(float) / mc).where(~S.FIN.astype(bool))
    ev = mc + S.DEBT.astype(float).fillna(0) - S.CASH.astype(float).fillna(0)
    S['ebitda_ev'] = (S.EBITDA4.astype(float) / ev).where(~S.FIN.astype(bool) & (ev > 0))
    S['fcf_yield'] = ((S.CFO4.astype(float) - S.CAPEX4.astype(float).abs()) / mc).where(~S.FIN.astype(bool))
    S['small_cap'] = -np.log(mc.astype(float))
    S['days_since_pub'] = (D - pd.to_datetime(S.avail)).dt.days
    return S
PF = ['ep', 'bp', 'sp', 'cfp', 'ebitda_ev', 'fcf_yield', 'small_cap']
# trailing 12-month dividend yield from the adjusted/raw close ratio
_r = (AD / CL); _dy = (1 - _r.shift(1) / _r).clip(lower=0); _dy = _dy.where(_dy > 0.002, 0)
DY = _dy.rolling(252, min_periods=200).sum()
if __name__ == '__main__':
    print(len(Q), 'ticker-quarters;', Q.ticker.nunique(), 'tickers; pub date known %.0f%%' % (100 * Q.pub_known.mean()))
    bad = Q[(ratio > 1.4) | (ratio < 0.7)]; print('split-guard rows', len(bad), bad.groupby('ticker').size().to_dict())
    S = snapshot(len(idx) - 1); print(S[['period', 'avail', 'mcap', 'ep', 'bp', 'roe', 'd_ni', 'sue', 'fscore']].round(3).to_string())
