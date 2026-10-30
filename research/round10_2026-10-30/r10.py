import os,sys; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,H); from lib import *
from pre_session import B as PRE, ALL
ETF=pd.read_csv(R+'/data/prices/ETFBW20TR.csv',parse_dates=['date']).set_index('date')['adj_close'].reindex(idx).ffill()
def eff(d,tm):
    d=pd.Timestamp(d); j=idx.searchsorted(d)
    if j<len(idx) and idx[j]==d and tm in('b','d'): return j
    return j if (j<len(idx) and idx[j]!=d) else j+1
T=[]  # (rule,ticker,i0,i1,cost)
# Asbis accel>0
S=pd.read_csv(os.path.join(H,'asbis_sales.csv'),parse_dates=['date']); S['acc']=S.yoy-S.yoy.shift(1).rolling(3).mean()
for k in range(3,len(S)):
    if S.acc[k]>0:
        i0=eff(S.date[k],S.timing[k]); i1=eff(S.date[k+1],S.timing[k+1]) if k+1<len(S) else len(idx)-1
        T.append(('Asbis','ASB',i0,min(i1,len(idx)-1),1.5))
# Results drift +3..6% L1, skip XTB
for t,s in PRE.items():
    if t not in L1 or t=='XTB' or t not in AD: continue
    alld=[idx.searchsorted(d) for d in pd.to_datetime(['20'+x for x in ALL.get(t,'').split()])]
    for d in pd.to_datetime(['20'+x for x in s.split()]):
        i=idx.searchsorted(d)
        if i>=len(idx) or i<1 or idx[i]!=d or any(0<i-j<=30 for j in alld): continue
        re=(AD[t].iloc[i]/AD[t].iloc[i-1]-1)*100-(W.iloc[i]/W.iloc[i-1]-1)*100
        if 3<=re<=6: T.append(('Drift',t,i,min(i+21,len(idx)-1),1.0))
# Biedronka -> Dino (LFL improved >0)
Bd=pd.read_csv(os.path.join(H,'biedronka_lfl.csv'),parse_dates=['date'])
for k in range(1,len(Bd)):
    if Bd.lfl[k]-Bd.lfl[k-1]>0:
        i0=idx.searchsorted(Bd.date[k],side='right') if Bd.timing[k]=='a' else eff(Bd.date[k],Bd.timing[k])
        T.append(('Dino','DNP',i0,min(i0+21,len(idx)-1),1.0))
# Car parts accel>5
C=pd.read_csv(R+'/data/carparts_sales.csv'); C['date']=pd.to_datetime(C.date)
for t in ('CAR','APR'):
    s=C[C.ticker==t].copy(); s['yoy_pct']=s.yoy_pct.fillna((s.sales_pln_m/s.sales_prev_year_pln_m-1)*100)
    s=s.dropna(subset=['yoy_pct']).sort_values('date').drop_duplicates('period').reset_index(drop=True)
    s['acc']=s.yoy_pct-s.yoy_pct.shift(1).rolling(3).mean()
    for k in range(3,len(s)):
        if s.acc[k]>5:
            i0=eff(s.date[k],s.session_timing[k][0])+1; i1=eff(s.date[k+1],s.session_timing[k+1][0]) if k+1<len(s) else len(idx)-1
            if i1>i0: T.append(('Carparts',t,i0,min(i1,len(idx)-1),1.0))
T=sorted(T,key=lambda x:x[2])
def sim(rules,K,start='2019-02-01',dep=5.4):
    s0=idx.searchsorted(pd.Timestamp(start)); cash=1.0; slots=[]  # slot: (rule,t,i0,i1,alloc)
    eq=[]; inv=[]; taken={}
    trades=[x for x in T if x[0] in rules and x[2]>=s0]
    ti=0; dd=(1+dep/100)**(1/252)-1
    for i in range(s0,len(idx)):
        # close positions
        keep=[]
        for (r,t,a,b,c,amt) in slots:
            if i==b:
                v=amt*AD[t].iloc[b]/AD[t].iloc[a]*(1-c/200); cash+=v; taken.setdefault(r,[]).append((AD[t].iloc[b]/AD[t].iloc[a]-1)*100-c)
            else: keep.append((r,t,a,b,c,amt))
        slots=keep
        # value
        val=cash+sum(amt*AD[t].iloc[i]/AD[t].iloc[a] for (r,t,a,b,c,amt) in slots if np.isfinite(AD[t].iloc[i]))
        # open new
        while ti<len(trades) and trades[ti][2]<=i:
            r,t,a,b,c=trades[ti]; ti+=1
            if a!=i or len(slots)>=K or any(x[1]==t for x in slots) or not np.isfinite(AD[t].iloc[a]): continue
            amt=min(cash,val/K); 
            if amt<=0: continue
            cash-=amt; slots.append((r,t,a,b,c,amt*(1-c/200)))
        cash*=1+dd
        val=cash+sum(amt*AD[t].iloc[i]/AD[t].iloc[a] for (r,t,a,b,c,amt) in slots if np.isfinite(AD[t].iloc[i]))
        eq.append(val); inv.append(1-cash/val)
    e=pd.Series(eq,index=idx[s0:]); yrs=len(e)/252
    etf=(ETF.iloc[s0:]/ETF.iloc[s0]); 
    cagr=(e.iloc[-1])**(1/yrs)-1; ecagr=etf.iloc[-1]**(1/yrs)-1
    mdd=(e/e.cummax()-1).min(); emdd=(etf/etf.cummax()-1).min()
    ys=e.resample('YE').last().pct_change(); ys.iloc[0]=e.resample('YE').last().iloc[0]-1
    ye=etf.resample('YE').last().pct_change(); ye.iloc[0]=etf.resample('YE').last().iloc[0]-1
    ntr=sum(len(v) for v in taken.values())
    print(f"{'+'.join(rules):32s} K={K}: {cagr*100:5.1f}%/yr (ETF {ecagr*100:4.1f}%) | worst fall {mdd*100:5.1f}% (ETF {emdd*100:5.1f}%) | invested {np.mean(inv)*100:3.0f}% of time-capital | trades {ntr} | years beating ETF {int((ys.values>ye.values).sum())}/{len(ys)}")
    return e,ys,ye,taken
print("trades available:",pd.Series([x[0] for x in T if x[2]>=idx.searchsorted(pd.Timestamp('2019-02-01'))]).value_counts().to_dict())
for rules in (['Asbis','Drift','Dino','Carparts'],['Asbis','Drift','Dino'],['Asbis'],['Drift'],['Carparts']):
    for K in (3,5):
        e,ys,ye,tk=sim(rules,K)
e,ys,ye,tk=sim(['Asbis','Drift','Dino','Carparts'],4)
print(pd.DataFrame({'portfolio %':(ys*100).round(1).values,'ETF %':(ye*100).round(1).values},index=ys.index.year).T.to_string())
print({k:(len(v),round(np.mean(v),2)) for k,v in tk.items()})
