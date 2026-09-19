#!/usr/bin/env python3
"""Read selected result metadata from pinned HF commits; never save credentials."""
import argparse, concurrent.futures, datetime, json, pathlib, urllib.request, urllib.parse, time, re
REPO='gvc-agent-analysis/benchmark-results'
OUT=pathlib.Path('/home/jiacheng/iclr2027_paper/data/hf_refresh')
def token():
 e={}
 for line in pathlib.Path('/data1/jiacheng/mas/hf.env').read_text().splitlines():
  if '=' in line and not line.strip().startswith('#'):
   k,v=line.strip().removeprefix('export ').split('=',1);e[k]=v.strip().strip('\"\'')
 return e.get('HF_TOKEN') or e.get('HUGGINGFACE_TOKEN')
TOKEN=token()
def fetch(url,path=None):
 for i in range(12):
  try:
   req=urllib.request.Request(url,headers={'Authorization':'Bearer '+TOKEN,'User-Agent':'paper-results-refresh/1'})
   with urllib.request.urlopen(req,timeout=45) as r: data=r.read()
   if path:path.parent.mkdir(exist_ok=True,parents=True);path.write_bytes(data)
   return json.loads(data)
  except Exception as ex:
   if getattr(ex,'code',None)==404:return None
   if i==11:raise
   if getattr(ex,"code",None)==429:
    t=re.search(r";t=(\d+)",ex.headers.get("RateLimit", ""))
    delay=min(45,int(t.group(1))+1) if t else 30
    print(f"HF resolver quota busy; retrying after {delay}s",flush=True)
    time.sleep(delay)
   else:time.sleep(min(10,2*(i+1)))
def getfile(branch,path):
 name=branch['name'].replace('/','__')
 return fetch(f'https://huggingface.co/datasets/{REPO}/resolve/{branch["targetCommit"]}/{path}',OUT/name/path)
def tree(branch,path=''):
 return fetch(f'https://huggingface.co/api/datasets/{REPO}/tree/{branch["targetCommit"]}/{path}')
def process(branch):
 name=branch['name']; rec={'branch':name,'commit':branch['targetCommit'],'jobs':[],'interpretation_files':[]}
 idx=getfile(branch,'MANIFEST_INDEX.json'); seg=idx.get('segments',{}).get(name.split('/')[-1],{}) if idx else {}
 rec['segment']=seg
 for root in ['data','interpretation']:
  for ent in tree(branch,root) or []:
   if ent['type']!='directory':continue
   for sub in tree(branch,ent['path']) or []:
    if root=='interpretation':
     if sub['type']=='file' and sub['path'].endswith(('.md','run_policy.json')):
      getfile(branch,sub['path']);rec['interpretation_files'].append(sub['path'])
    elif sub['type']=='directory':
     jobpath=sub['path'];d=getfile(branch,jobpath+'/result.json')
     if d is not None:
      c=getfile(branch,jobpath+'/config.json')
      ev={}
      for k,v in d.get('stats',{}).get('evals',{}).items():
       ev[k]={a:b for a,b in v.items() if a not in ('reward_stats','exception_stats')}
       ev[k]['reward_counts']={a:{val:len(ids) for val,ids in vals.items()} for a,vals in v.get('reward_stats',{}).items()}
       ev[k]['exception_counts']={a:len(ids) for a,ids in v.get('exception_stats',{}).items()}
      rec['jobs'].append({'path':jobpath,**{k:v for k,v in d.items() if k!='stats'},'stats':{k:v for k,v in d.get('stats',{}).items() if k!='evals'},'evals':ev})
     else:rec['jobs'].append({'path':jobpath,'missing_job_result':True})
 return rec
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--branches',default='');p.add_argument('--workers',type=int,default=3);a=p.parse_args()
 refs=fetch(f'https://huggingface.co/api/datasets/{REPO}/refs',OUT/'refs.json')
 branches=[x for x in refs['branches'] if x['name']!='main' and (not a.branches or x['name'].split('/')[-1] in a.branches.split(','))]
 records=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
  fs={pool.submit(process,b):b for b in branches}
  for f in concurrent.futures.as_completed(fs):
   try:
    r=f.result();records.append(r);print(r['branch'],json.dumps(r['jobs']),flush=True)
   except Exception as ex:print(fs[f]['name'],'ERROR',type(ex).__name__,str(ex),flush=True)
 payload={'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repo':REPO,'branches':records}
 (OUT/('summary'+('_selected' if a.branches else '')+'.json')).write_text(json.dumps(payload,indent=2))
