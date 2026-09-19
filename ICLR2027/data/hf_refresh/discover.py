import importlib.util,concurrent.futures,json
s=importlib.util.spec_from_file_location('f','/home/jiacheng/iclr2027_paper/scripts/fetch_hf_results.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
refs=json.loads((m.OUT/'refs.json').read_text())
wanted=['chembench_openweb_150','elaipbench_rerun4','stark_rerun7','test_of_time_arm2','sstqa']
for b in refs['branches']:
 if b['name'].split('/')[-1] not in wanted:continue
 jobs=[]
 for x in m.tree(b,'data') or []:
  if x['type']=='directory':
   for y in m.tree(b,x['path']) or []:
    if y['type']=='directory':jobs.append(y['path'])
 print(b['name'],jobs,flush=True)
 (m.OUT/(b['name'].replace('/','__')+'_jobs.json')).write_text(json.dumps({'branch':b,'jobs':jobs},indent=2))
