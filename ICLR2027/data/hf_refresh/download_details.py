import importlib.util,json,concurrent.futures
s=importlib.util.spec_from_file_location('f','/home/jiacheng/iclr2027_paper/scripts/fetch_hf_results.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
d=json.loads((m.OUT/'new_jobs.json').read_text());requests=[]
for b in d['branches']:
 j=b['jobs'][0];rs=next(iter(j['result']['stats']['evals'].values()))['reward_stats']['reward'];ids=[x for a in rs.values() for x in a]
 if 'rerun' in b['branch']: selected=ids
 elif 'sstqa' in b['branch']:selected=[ids[0],ids[-1],'sstqa-00443__bfody5i']
 elif 'chembench' in b['branch']:selected=[ids[0],ids[-1]]
 else:continue
 for i in selected:
  for f in ['verifier/detail.json','result.json']:
   requests.append(({'name':b['branch'],'targetCommit':b['commit']},j['path']+'/'+i+'/'+f))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for b,p in requests:pool.submit(m.getfile,b,p)
print('Downloaded',len(requests),'small verifier/trial artifacts')
