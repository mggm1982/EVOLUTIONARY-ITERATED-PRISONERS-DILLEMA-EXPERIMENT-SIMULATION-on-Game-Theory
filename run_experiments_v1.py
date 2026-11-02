from pathlib import Path
import subprocess, csv, json, statistics, collections
from concurrent.futures import ThreadPoolExecutor
base=Path(__file__).parent
exe=base/'code/epd_batch'
R=base/'results';R.mkdir(exist_ok=True)
seeds=[101,202,303,404,505,606,707,808,909,1010]
configs=[]
def add(group,name,**kwargs):
 p={'rounds':30,'gens':250,'alpha':0.05,'error':0.0,'forgiveness':0.0,'pop':[120]*5}
 p.update(kwargs); configs.append((group,name,p))
add('baseline','noise_free')
for e in [0,0.02,0.05,0.10,0.20]:add('errors',f'error_{e:.2f}',error=e,forgiveness=0.0)
for f in [0,0.05,0.10,0.25,0.50]:add('forgiveness',f'forgive_{f:.2f}',error=0.08,forgiveness=f)
for a in [0,0.01,0.03,0.05,0.10,0.50,1.0]:add('selection',f'alpha_{a:.2f}',alpha=a,error=0.04,forgiveness=0.05)
for name,p in [('equal',[120]*5),('cooperation_heavy',[180,180,180,30,30]),('defection_heavy',[60,60,60,360,60]),('random_heavy',[60,60,60,60,360])]:add('initial',name,error=0.04,forgiveness=0.05,pop=p)
for name,rounds in [('rounds_20',20),('rounds_30',30),('rounds_50',50)]:add('rounds',name,error=0.04,forgiveness=0.05,rounds=rounds)
def one(task):
 group,name,p,seed=task
 dest=R/group/name/f'seed_{seed}.csv';dest.parent.mkdir(parents=True,exist_ok=True)
 if not dest.exists() or dest.stat().st_size < 150:
  cmd=[str(exe),str(seed),str(p['rounds']),str(p['gens']),str(p['alpha']),str(p['error']),str(p['forgiveness']),*[str(v) for v in p['pop']],str(dest)]
  result=subprocess.run(cmd,capture_output=True,text=True)
  if result.returncode:raise RuntimeError(result.stderr)
 with dest.open() as f:rows=list(csv.DictReader(f))
 if len(rows) != p['gens']+1:
  dest.unlink(missing_ok=True)
  return one(task)
 final=rows[-1]
 rec={'group':group,'configuration':name,'seed':seed,'rounds':p['rounds'],'generations':p['gens'],'alpha':p['alpha'],'error':p['error'],'forgiveness':p['forgiveness'],'initial':','.join(map(str,p['pop']))}
 total=sum(p['pop'])
 for k in ['TFT','GT','AC','AD','RANDOM']:
  rec[k]=round(int(final[k])/total*100,3)
  rec[k+'_extinction']=next((int(row['generation']) for row in rows if int(row[k])==0),None)
 rec['winner']=max(['TFT','GT','AC','AD','RANDOM'],key=lambda x:rec[x])
 return rec
with ThreadPoolExecutor(max_workers=10) as pool:
 records=list(pool.map(one,[(g,n,p,seed) for g,n,p in configs for seed in seeds]))
with (R/'run_summary.csv').open('w',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=records[0].keys());wr.writeheader();wr.writerows(records)
groups=collections.defaultdict(list)
for rec in records:groups[(rec['group'],rec['configuration'])].append(rec)
means=[]
for (group,name),rs in groups.items():
 item={'group':group,'config':name,'n':len(rs)}
 for k in ['TFT','GT','AC','AD','RANDOM']:
  item[k+'_mean']=round(statistics.mean(r[k] for r in rs),2)
  item[k+'_sd']=round(statistics.stdev(r[k] for r in rs),2)
 item['winner_counts']=dict(collections.Counter(r['winner'] for r in rs))
 means.append(item)
(R/'aggregate.json').write_text(json.dumps(means,indent=2))
with (R/'aggregate.csv').open('w',newline='') as f:
 fields=['group','config','n']+[suffix for k in ['TFT','GT','AC','AD','RANDOM'] for suffix in [k+'_mean',k+'_sd']]
 wr=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');wr.writeheader();wr.writerows(means)
print(f'Completed {len(records)} runs, {len(configs)} configurations')
for m in means:
 print(m['group'],m['config'],*[f'{k}:{m[k+"_mean"]:.1f}±{m[k+"_sd"]:.1f}' for k in ['TFT','GT','AC','AD','RANDOM']])
