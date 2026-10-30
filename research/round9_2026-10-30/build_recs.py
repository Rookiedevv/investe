import csv, glob, os, re, sys, datetime as dt
from collections import Counter
RAW = sys.argv[1]; OUT = sys.argv[2]
SLUG = {'PKO':'pkobp','PEO':'pekao','PZU':'pzu','KGH':'kghm','PKN':'pknorlen','ALE':'allegro','DNP':'dinopl',
 'CDR':'cdprojekt','LPP':'lpp','XTB':'xtb','ZAB':'zabka','PCO':'pepco','PGE':'pge','ACP':'assecopol','TPE':'tauronpe',
 'MBK':'mbank','ALR':'alior','KTY':'kety','BDX':'budimex','KRU':'kruk','OPL':'orangepl','JSW':'jsw','MIL':'millennium',
 'SNT':'synektik','CPS':'cyfrplsat','ING':'ingbsk','ENA':'enea','APR':'autopartn','CAR':'intercars','EBP':'erstepl',
 'DIA':'diag','BHW':'handlowy','DOM':'domdev','VRG':'vrg','11B':'11bit','TEN':'tsgames','PXM':'polimexms'}
def broker(s):
    s=s.strip(); l=s.lower()
    rules=[('bo','DM BOŚ',['boś','bos dm','dm bos']),('tr','DM Trigon',['trigon']),('mb','BM mBank',['mbank']),
      ('nb','Noble Securities',['noble']),('ml','DM Millennium',['millennium']),('bdm','DM BDM',['bdm']),
      ('ip','Ipopema Securities',['ipopema']),('evr','East Value Research',['east value']),('ht','Haitong Bank',['haitong']),
      ('vs','Vestor DM',['vestor']),('st','Santander BM',['santander']),('er','Erste Group',['erste']),
      ('gs','Goldman Sachs',['goldman']),('hs','HSBC',['hsbc']),('wd','Wood & Company',['wood']),
      ('bps','DM Banku BPS',['bps']),('pk','BM Pekao',['pekao'])]
    for _,name,keys in rules:
        if any(k in l for k in keys): return name
    return s
def num(x):
    x=(x or '').replace('zł','').replace('\xa0','').replace(' ','').replace('"','').strip()
    if not x: return None
    x=x.replace(',','.'); return float(x)
def d(x): return dt.date.fromisoformat(x[:10]) if x else None
recs=[]  # dicts
drops=[]; flagged=[]
for f in sorted(glob.glob(os.path.join(RAW,'sw_*.csv'))):
    t=os.path.basename(f)[3:-4]
    for row in csv.reader(open(f,encoding='utf-8')):
        if not row: continue
        b,r,tg,dd,px=(row+['']*6)[:5]
        if dd<'2018-01-01': drops.append((t,row,'pre-2018 bogus date')); continue
        if t=='MBK' and 'mbank' in b.lower() and dd=='2025-10-31': drops.append((t,row,'Pekao rec misassigned to mBank')); continue
        rec=dict(ticker=t,broker=broker(b),rating=r.strip().lower(),target=num(tg),price=num(px),issue=d(dd),pub=None,
                 src={'stockwatch':f'https://www.stockwatch.pl/gpw/{SLUG[t]},rekomendacje,wskazniki.aspx'},sw=True)
        recs.append(rec)
# biznesradar
br=[]
for line in open(os.path.join(RAW,'br_all.txt'),encoding='utf-8'):
    p=line.strip().split('|')
    if len(p)<6: continue
    br.append(dict(ticker=p[0],rating=p[1].lower(),target=num(p[2]),price=num(p[3]),pub=d(p[4]),broker=broker(p[5]),issue=None))
sf=[]
for line in open(os.path.join(RAW,'sf_all.txt'),encoding='utf-8'):
    p=line.rstrip('\n').split('|')
    if len(p)<6: continue
    sf.append(dict(ticker=p[0],rating=p[1].lower(),target=num(p[2]),broker=broker(p[3]),pub=d(p[4]),issue=d(p[5]) if p[5] else None))
def close(a,b,tol=0.02): return a and b and abs(a-b)/b<=tol
def match(rec, x, maxlag=14):
    if rec['ticker']!=x['ticker'] or rec['broker']!=x['broker']: return None
    ri = rec['issue'] or rec.get('pub'); xd = x['issue'] or x['pub']
    if not ri or not xd: return None
    gap=(xd-ri).days
    if rec.get('pub') and x['pub']: gap=(x['pub']-rec['pub']).days
    if abs(gap)>maxlag: return None
    if close(rec['target'],x['target']): return abs(gap)
    # biznesradar values are dividend/split-adjusted: same rec if target/price scale factors agree
    if abs(gap)<=1 and rec['target'] and x['target'] and rec.get('price') and x.get('price'):
        if abs(x['target']/rec['target'] - x['price']/rec['price'])<0.01: return abs(gap)+0.25
    if abs(gap)<=1 and rec['rating']==x['rating']: return abs(gap)+0.5
    return None
# merge biznesradar into stockwatch
BRURL='https://www.biznesradar.pl/rekomendacje/'; SFURL='https://strefainwestorow.pl/rekomendacje/lista-rekomendacji'
conflicts=[]
def merge(srcname, items, url):
    for x in items:
        cands=[(m,r) for r in recs if (m:=match(r,x)) is not None and srcname not in r['src']]
        if cands:
            m,r=min(cands,key=lambda c:c[0])
            if r['target'] and x['target'] and not close(r['target'],x['target'],0.005):
                conflicts.append((r['ticker'],r['broker'],str(r['issue'] or r['pub']),r['target'],srcname,x['target']))
            if x['rating'] and r['rating'] and x['rating']!=r['rating'] and not (x['rating'].startswith('neutral') and r['rating'].startswith('neutral')):
                conflicts.append((r['ticker'],r['broker'],str(r['issue'] or r['pub']),'rating',r['rating'],srcname,x['rating']))
            if srcname=='strefa':
                r['target']=x['target'] or r['target']
                if x['rating']: r['rating']=x['rating']
            else:
                r['target']=r['target'] or x['target']
                r['rating']=r['rating'] or x['rating']
            if srcname=='biznesradar':
                r['pub']=x['pub']
                if not r['price']: r['price']=x['price']
            else:
                r['pub_sf']=x['pub']
                if x['issue'] and not r['issue']: r['issue']=x['issue']
            r['src'][srcname]=url
        else:
            n=dict(ticker=x['ticker'],broker=x['broker'],rating=x['rating'],target=x['target'],
                   price=x.get('price') if srcname=='biznesradar' else None,issue=x['issue'],
                   pub=x['pub'] if srcname=='biznesradar' else None,src={srcname:url},sw=False)
            if srcname=='strefa': n['pub_sf']=x['pub']
            recs.append(n)
merge('biznesradar',br,BRURL)
merge('strefa',sf,SFURL)
# pub_date: strefa public date preferred (later, conservative), else biznesradar
lags=[]
for r in recs:
    pb=r.get('pub'); ps=r.get('pub_sf')
    r['pub_final']=ps or pb
    if r['issue'] and r['pub_final']: lags.append(((r['pub_final']-r['issue']).days, 'sf' if ps else 'br', r['ticker'],r['broker']))
    if r['target'] and r['price']:
        q=r['target']/r['price']
        if q>3 or q<0.3:
            flagged.append((r['ticker'],r['broker'],str(r['issue']),r['target'],r['price'])); r['target']=None
# dedupe
seen=set(); out=[]
for r in sorted(recs,key=lambda r:(r['ticker'],str(r['pub_final'] or r['issue']),r['broker'])):
    k=(r['ticker'],r['broker'],r['issue'] or r['pub_final'],r['target'],r['rating'])
    if k in seen: drops.append((r['ticker'],k,'dup')); continue
    seen.add(k); out.append(r)
def fmt(v):
    if v is None: return ''
    return ('%.4f'%v).rstrip('0').rstrip('.')
with open(OUT,'w',newline='',encoding='utf-8') as fh:
    w=csv.writer(fh); w.writerow(['ticker','pub_date','issue_date','broker','rating','prev_rating','target','prev_target','price_on_issue','source_url'])
    for r in out:
        w.writerow([r['ticker'],r['pub_final'] or '',r['issue'] or '',r['broker'],r['rating'],'',fmt(r['target']),'',fmt(r['price']),' ; '.join(r['src'].values())])
print('rows',len(out))
ds=[r['issue'] or r['pub_final'] for r in out]; print('range',min(ds),max(ds))
print('per ticker',sorted(Counter(r['ticker'] for r in out).items(),key=lambda x:-x[1]))
print('with pub_date',sum(1 for r in out if r['pub_final']),'with issue',sum(1 for r in out if r['issue']),'both',sum(1 for r in out if r['pub_final'] and r['issue']))
print('lags',sorted(lags))
print('br-vs-issue', sorted(((r['pub']-r['issue']).days) for r in out if r.get('pub') and r['issue']))
print('sf-vs-br', sorted(((r['pub_sf']-r['pub']).days) for r in out if r.get('pub') and r.get('pub_sf')))
print('conflicts',conflicts); print('flagged(target blanked)',flagged); print('drops',[x for x in drops if x[2]!='dup'], 'dups',sum(1 for x in drops if x[2]=='dup'))
print('blank rating',sum(1 for r in out if not r['rating']))
print('sources',Counter(tuple(sorted(r['src'])) for r in out))
