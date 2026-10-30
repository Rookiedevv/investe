from lib import *
R1=AD.pct_change(fill_method=None)*100; WR=W.pct_change()*100
EX=R1.sub(WR,axis=0)
VR=VO/VO.rolling(60,min_periods=40).median().shift(1)
liq=[t for t in TICK if t in LIQ]
def ev(mask,H=21,short=False,gap=10):
    rows=[]
    for t in liq:
        ii=np.where(mask[t].fillna(False).values)[0]; last=-999
        for i in ii:
            if i-last<gap or i+H>=len(idx): continue
            last=i; rows.append(trade(t,i,i+H,short))
    return rows
base=summ(ev(EX.abs()<99,21,gap=21),"baseline: any day, hold 21")
summ(ev((VR>=3)&(EX.abs()<1.5)),"volume >=3x, quiet price (|exc|<1.5%), buy, 21")
summ(ev((VR>=3)&(EX.abs()<1.5),short=True),"   same, XTB short")
summ(ev((VR>=3)&(EX>=2)&(EX<6)),"volume >=3x, up +2..6% vs W20, buy, 21")
summ(ev((VR>=3)&(EX>=6)),"volume >=3x, up >=6%, buy, 21")
summ(ev((VR>=3)&(EX>=6),short=True),"   same, XTB short")
summ(ev((VR>=3)&(EX<=-2)&(EX>-6)),"volume >=3x, down -2..-6%, buy, 21")
summ(ev((VR>=3)&(EX<=-2)&(EX>-6),short=True),"   same, XTB short")
summ(ev((VR<=0.4)),"very low volume day (<=0.4x), buy, 21")
# 52-week high / low
HI=AD.rolling(252,min_periods=240).max(); LO=AD.rolling(252,min_periods=240).min()
newhi=(AD>=HI)&(AD.shift(1)<HI.shift(1))
newlo=(AD<=LO)&(AD.shift(1)>LO.shift(1))
summ(ev(newhi,gap=21),"first close at new 52w high, buy, 21")
summ(ev(newhi&(VR>=2),gap=21),"new 52w high on >=2x volume, buy, 21")
summ(ev(newlo,gap=21,short=True),"first close at new 52w low, XTB short, 21")
summ(ev(newlo,gap=21),"first close at new 52w low, buy, 21")
