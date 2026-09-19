import importlib.util,json,urllib.request,urllib.error,datetime
s=importlib.util.spec_from_file_location('f','/home/jiacheng/iclr2027_paper/scripts/fetch_hf_results.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
records=[]
for p in sorted(m.OUT.glob('*_jobs.json')):
 a=json.loads(p.read_text());b=a['branch']; rec={'branch':b['name'],'commit':b['targetCommit'],'jobs':[]}
 for path in a['jobs']:
  d=m.getfile(b,path+'/result.json');c=m.getfile(b,path+'/config.json');rec['jobs'].append({'path':path,'result':d,'config':c})
  print(b['name'],{k:v for k,v in d.items() if k!='stats'},[(k,v['metrics'],v.get('n_trials'),v.get('n_errors')) for k,v in d['stats']['evals'].items()],flush=True)
 records.append(rec)
 (m.OUT/'new_jobs.json').write_text(json.dumps({'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'branches':records},indent=2))
