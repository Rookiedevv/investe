# Merge the two scraped KNF register files into one table: holder, issuer, pct, pos_date (position date), update_date (where known).
import os,re,csv; H=os.path.dirname(os.path.abspath(__file__))
rows=[]
for r in csv.DictReader(open(os.path.join(H,'knf_hist_part1.csv'))):
    rows.append((r['holder'].strip(),r['issuer'].strip(),float(r['pct']),r['pos_date'],r['update_date']))
hold=iss=None
for line in open(os.path.join(H,'knf_hist_part2.txt')):
    line=line.strip()
    if not line or line.startswith('#'): continue
    if line.startswith('H='):
        m=re.match(r'H=(.*);I=(.*)',line); hold,iss=m.group(1).strip(),m.group(2).strip(); continue
    for pair in line.split(';'):
        p=pair.split()
        if len(p)==2: rows.append((hold,iss,float(p[0]),p[1],''))
rows=sorted(set(rows),key=lambda x:(x[1],x[0],x[3]))
with open(os.path.join(H,'knf_hist.csv'),'w') as f:
    w=csv.writer(f); w.writerow(['holder','issuer','pct','pos_date','update_date']); w.writerows(rows)
print(len(rows),'rows;',len({r[1] for r in rows}),'issuers;',len({r[0] for r in rows}),'holders')
import collections; print(collections.Counter(r[1] for r in rows).most_common())
