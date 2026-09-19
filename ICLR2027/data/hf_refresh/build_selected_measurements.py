import pathlib,json,statistics,hashlib,math,datetime,shutil
ROOT=pathlib.Path('/home/jiacheng/iclr2027_paper/data/hf_refresh'); MIRROR=pathlib.Path('/data1/jiacheng/mentor_results')
refs={b['name']:b['targetCommit'] for b in json.loads((ROOT/'refs.json').read_text())['branches']}
new=json.loads((ROOT/'new_jobs.json').read_text())['branches']; old=json.loads((ROOT/'local_aggregates.json').read_text())['branches']
def path_for(branch):
 matches=[]
 for base in [ROOT,MIRROR/'branches_http',MIRROR/'branches',MIRROR/'benchmark-results']:
  matches+=list((base/branch.replace('/','__')).glob('data/*/*/result.json'))
 if not matches:raise ValueError(branch)
 return matches[0]
def source(branch):
 p=path_for(branch);branch_root=next(a for a in p.parents if a.name==branch.replace('/','__'));rel=p.relative_to(branch_root).as_posix();dest=ROOT/branch.replace('/','__')/rel
 if p!=dest:dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 return {'branch':branch,'commit':refs[branch],'result_path':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'url':f'https://huggingface.co/datasets/gvc-agent-analysis/benchmark-results/blob/{refs[branch]}/{rel}'}
def rewards(branch):
 d=json.loads(path_for(branch).read_text());r={}
 for e in d['stats']['evals'].values():
  for value,ids in e['reward_stats'].get('reward',{}).items():
   for id in ids:r[id.split('__')[0]]=float(value)
 return r,d
rows=[]
def add(slug,branches,metric,notes='',aggregation='micro',role='suite'):
 rs={};sources=[];replacement={}
 for branch in branches:
  r,d=rewards(branch);replacement[branch]=sorted(set(rs)&set(r));rs.update(r);sources.append(source(branch))
 n=len(rs);mean=statistics.mean(rs.values());binary=set(rs.values())<={0.,1.};se=statistics.stdev(rs.values())/math.sqrt(n) if n>1 else 0
 ci=None
 if binary:
  z=1.959963984540054;den=1+z*z/n;center=(mean+z*z/(2*n))/den;half=z*math.sqrt(mean*(1-mean)/n+z*z/(4*n*n))/den;ci=[(center-half)*100,(center+half)*100]
 row={'slug':slug,'role':role,'score':100*mean,'n':n,'metric':metric,'aggregation':aggregation,'successes':sum(rs.values()) if binary else None,'se':100*se,'ci95':ci,'ci_method':'Wilson' if binary else None,'per_task_rewards':rs,'sources':sources,'replacement_ids':replacement,'notes':notes}
 rows.append(row);return row
add('stark',['backup/stark','backup/stark_rerun7'],'Hit@1','Merged seven previously ungraded task IDs; all2801 registered tasks have native rewards. Original timeout task00511 counts0; it is not a preflight failure.')
add('elaipbench',['backup/elaipbench','backup/elaipbench_rerun4'],'accuracy','Four rerun IDs replace failed original executions, all0/4; native parser empty for42/252 and wrongparsed answers for43/251.')
add('chembench',['backup/chembench_openweb_150'],'overall_score','Completed planned150-task subset;113 successes, no execution errors. web_search=live; mediumreasoning, Codex0.149.1. Published reference covers larger benchmark, label subset.')
add('oolong',['backup/oolong_labels_off_192'],'labels-off score','Full192 labels-off in-prompt test split; fractional graded metric, binomial/Wilson interval is inappropriate.')
add('multihiertt',['backup/multihiertt'],'accuracy','Owner-selected denominator1044; native grader744 successes. Historical1042 denominator retired.')
add('llm_srbench',['backup/llm_srbench'],'acc_0.1 (worst-point, pass@1)','Registered129 denominator gives116/12989.92%; historical measured127 denominator gives91.34%, should not conflate.')
add('test_of_time_arm2',['backup/test_of_time_arm2'],'accuracy','Complete280-task alternative arm,274successes; separate from original baseline, do not silently overwrite.','micro','supplementary_ablation')
add('sstqa',['backup/sstqa'],'accuracy (ST-Raptor prompt; gpt-5.6-luna judge)','Completed764 English questions; native benchmark T/F prompt on azure/gpt-5.6-luna, unlike ASTRA policy GPT-5/astra_paper. Timeout443 still gradedcorrect. Do not pair against ASTRA509/764 without common-judge regrade.','micro','additional_measured_variant')
for slug,branch,groupkey in [('biomni_eval1','backup/biomni_eval1_tool_hosts','task_name'),('medagentsbench','backup/medagentsbench','subset')]:
 r=add(slug,[branch],'macro accuracy','',aggregation='macro');p=path_for(branch);groups={}
 # Per-trial detail source is the local mirror even if an aggregate was copied into ROOT.
 for base in [MIRROR/'branches_http',MIRROR/'branches',MIRROR/'benchmark-results']:
  jobs=list((base/branch.replace('/','__')).glob('data/*/*/result.json'))
  if jobs:
   job=jobs[0].parent;break
 for dp in job.glob('*/verifier/detail.json'):
  d=json.loads(dp.read_text());m=d.get('evaluator_record',{}).get('metrics',{});g=m.get(groupkey)
  if g is None and slug=='medagentsbench':g=m.get('dataset') or m.get('source_dataset')
  groups.setdefault(str(g),[]).append(float(d['reward']))
 r['groups']={k:{'n':len(v),'correct':sum(v),'mean':statistics.mean(v)} for k,v in groups.items()};r['score']=100*statistics.mean(statistics.mean(v) for v in groups.values());r['n']=sum(len(v) for v in groups.values());r['ci95']=None;r['ci_method']=None;r['se']=100*math.sqrt(sum(statistics.variance(v)/len(v) for v in groups.values()))/len(groups)
 r['successes']=None
 r['notes']='Mean of ten task accuracies;15-host tool rerun lacks official data lake; retain as measured variant.' if slug=='biomni_eval1' else 'Mean of nine subset accuracies;862 native grades, including missing-answer failures; historical n860 excluded two valid failures.'
result={'schema_version':1,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repo':'gvc-agent-analysis/benchmark-results','measurement_selection':'Latest completed new jobs, repaired baseline joins by task ID, and denominator/macro corrections. Each score retains actual protocol labels; inclusion in paper comparison is separate.','rows':rows}
(ROOT/'selected_measurements.json').write_text(json.dumps(result,indent=2))
for r in rows:print(r['slug'],r['score'],r['n'],r['groups'] if 'groups' in r else '')
