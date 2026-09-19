#!/usr/bin/env python3
"""Merge verified HF reruns into the paper, preserving the previous measurements.

This is a local-only operation. Remote retrieval, native-score extraction, and
scientific inclusion decisions are separate and preserved under data/hf_refresh.
"""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = Path('/data1/jiacheng/multiagent_repo_analysis/codex-generalization')
BASE = ROOT / 'data/history/results_snapshot_before_hf_refresh.json'
UPDATE = ROOT / 'data/hf_refresh/selected_measurements.json'
SUITE = ROOT / 'data/study_suite.json'

CAVEATS = {
    'stark': 'Seven recovered trials are merged by task ID with the original run: 2072/2801 = 73.97. The original timeout is counted as a scheduled-task failure. ARK48.20 is the selected published reference; tool and backbone differences remain.',
    'elaipbench': 'Four previously failed launches were re-executed and graded (0/4), yielding 151/403 = 37.47. Both the published-score row and the updated paired comparator table now use all403 instances. Published AgentSPEX used high effort; Codex and the shared-backbone medium comparator use medium.',
    'chembench': 'Completed, planned 150-question open-web subset, 113/150 = 75.33, with no execution errors. This is a scoped pilot against the full-benchmark paper reference, not completion of the 2785-question open-web evaluation. The earlier closed-web71.89 is preserved in the history.',
    'oolong': 'Completed192-question labels-off, in-prompt test-split rerun, score73.44. It replaces the incompatible100-question labels-on staged-file99.00. The official score has fractional credit; a binomial interval is inappropriate. The selected EnSI-RAG paper reference is71.84.',
    'multihiertt': 'Registered denominator1044, as explicitly selected in the September17 owner decision:744/1044 =71.26. The old1042 denominator is retired. Answer accuracy is the comparison metric, not the separate F1 column.',
    'llm_srbench': 'The scheduled129-task denominator gives116/129 =89.92, including two unmeasured/failed tasks as zero credit. The earlier91.34 is conditional on127 measured tasks. Both denominators are disclosed; the paper reference87.60 uses129.',
    'biomni_eval1': 'Completed September11 433-task rerun on the historical15-host tool surface. The ten-task macro is59.76; the job micro61.89 is not the Table1 metric. This is a retained scored variant: the official E1/data-lake arm remains pending. It is excluded only from the primary published-score tally, not removed from the score table.',
    'medagentsbench': 'All862 native grades contribute to the nine-subset macro50.51. The old860-row selection dropped two valid failures. This is a retained standalone Codex result; GSEM has no published nine-subset aggregate, so no aggregate reference is invented.',
    'matscibench': 'Retained text-only73.37 measurement over1025 questions under the documented retired15-host prompt and disabled built-in web search. This is a scored variant while the newly chosen open-web condition remains pending; it does not enter the primary published-score tally.',
    'insightbench': 'Retained conditional53.68 score on91 graded questions of100 under the older closed-web/old-judge setting. The new open-web100-question job has grader failures; its zero summary is not promoted to a performance result. The pinned-judge rescore remains pending.',
    'frontierscience_research': 'Retained closed-book, older-judge variant30/59 =50.85; the planned-set denominator60 would give50.00. The current target is open-book with the pinned GPT-5 judge, so it remains outside the primary published-score tally. FrontierAgent63.3 is the external reference.',
    'rarebench': 'No new repaired-network result was found in the current HF branches. The old161/370 =43.51 run had no successful retrieval and is retained only as diagnostic history. The primary score remains pending rather than being carried forward as a valid result.',
}


def main():
    data = json.loads(BASE.read_text())
    updates = json.loads(UPDATE.read_text())
    rows = {r['slug']: r for r in data['rows']}
    for row in rows.values():
        row['previous_measurement'] = {k: row.get(k) for k in ['score','n_measured','metric','ci95','se','reporting_status','caveat']}
        row['codex_role'] = 'primary' if row['include_in_provisional_external_summary'] or row['slug']=='medagentsbench' else 'variant'
        row['valid_codex_measurement'] = row['slug'] != 'rarebench'
        if row['codex_role']=='variant': row['reporting_status']='scored_variant'
        row['paired_comparator_complete'] = row['slug'] in ['financemath','elaipbench','industryor']
        row['measurement_provenance'] = {'source_type':'historical_dashboard','snapshot_date':'2026-09-09'}
    sst_policy_path = REPO / '3_deploy_run/quickstart/scenario1_specs/sstqa/run_policy.json'
    sst_policy = json.loads(sst_policy_path.read_text())
    for u in updates['rows']:
        if u['role']=='supplementary_ablation': continue
        slug=u['slug']
        if slug=='sstqa':
            rows[slug] = {'slug':slug,'name':'SSTQA','domain':'Semi-structured table QA','scale':[0,100],
                'current_reference':{'system':'ASTRA','backbone':'DeepSeek-V3','score':81.9,'paper':'arXiv2604.08999'},
                'historical_references':[], 'reporting_status':'scored_variant','codex_role':'variant',
                'valid_codex_measurement':True,'include_in_provisional_external_summary':False,
                'paired_comparator_complete':False,'metric_label':'Judge accuracy',
                'caveat':'English764-question result,590/764 =77.23, using the ST-Raptor benchmark T/F prompt with a gpt-5.6-luna judge. The September17 owner decision selects the Chinese split as the primary condition to align with ASTRA. This English result remains a declared language/judge variant; the Chinese primary run and aligned grading are pending. SSTQA replaces LongBench-v2 in the20-benchmark main suite.',
                'policy_source':str(sst_policy_path),'policy_sha256':hashlib.sha256(sst_policy_path.read_bytes()).hexdigest(),
                'current_selected_system_description':sst_policy['sota_system']}
            rows[slug]['figure_published_reference']=dict(rows[slug]['current_reference'])
        row=rows[slug]
        for source in u['sources']:
            assert Path(source['result_path']).is_file(), source['result_path']
            assert hashlib.sha256(Path(source['result_path']).read_bytes()).hexdigest()==source['sha256']
        row.update(score=u['score'], n_measured=u['n'], metric=u['metric'], ci95=u['ci95'],se=u['se'],
                   interval_description=(u['ci_method'] or 'No binary interval; retain the correct aggregation')+'; recomputed from selected native grades')
        row['measurement_provenance']={'source_type':'huggingface','repo':updates['repo'],
            'branch':u['sources'][-1]['branch'],'commit':u['sources'][-1]['commit'],
            'run_id':Path(u['sources'][-1]['result_path']).parent.name,'sources':u['sources'],
            'retrieved_at':updates['retrieved_at'],'aggregation':u['aggregation']}
        if 'groups' in u: row['aggregation_groups']=u['groups']
        if slug in ['stark','elaipbench','oolong','multihiertt','llm_srbench']:
            row.update(reporting_status='updated_baseline',codex_role='primary',include_in_provisional_external_summary=True)
        if slug=='chembench':
            row.update(reporting_status='planned_subset',codex_role='primary',include_in_provisional_external_summary=True)
        if slug=='medagentsbench': row.update(reporting_status='no_comparable_reference',codex_role='primary')
        if slug=='biomni_eval1': row.update(reporting_status='scored_variant',codex_role='variant')
        if slug in CAVEATS: row['caveat']=CAVEATS[slug]
    # Official CRAG empty-answer short circuit is a legitimate zero, not missing grading.
    crag_root=Path('/data1/jiacheng/mentor_results/branches/backup__crag/data/crag/crag__2026-09-04__12-15-01')
    crag_values=[]; crag_sources=[]
    for p in sorted(crag_root.glob('crag-*/verifier/detail.json')):
        detail=json.loads(p.read_text()); metrics=detail['evaluator_record']['metrics']
        crag_values.append(metrics['truthfulness'])
        crag_sources.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    assert len(crag_values)==578 and abs(sum(crag_values)-329)<1e-8
    rows['crag'].update(score=sum(crag_values)/578,n_measured=578,ci95=None,se=None,
        caveat='Retained pre-retrieved-KG variant: truthfulness329/578 =0.5692 (435 correct,106 hallucinations,37 missing). The old577 denominator wrongly excluded a valid empty-answer zero. The benchmark mock-API arm and aligned-judge comparison remain pending; paper0.711 is not the local regrade0.3893.',
        measurement_provenance={'source_type':'local_verifier_artifacts','run_id':crag_root.name,'source_root':str(crag_root),'sources':crag_sources})
    for slug in ['matscibench','insightbench','frontierscience_research','rarebench']: rows[slug]['caveat']=CAVEATS[slug]
    rows['rarebench'].update(score=None,ci95=None,se=None,codex_role='pending',reporting_status='invalid_measurement',valid_codex_measurement=False)
    rows['oolong']['metric_label']='Labels-off score'
    rows['biomni_eval1']['metric_label']='Task macro'
    rows['medagentsbench']['metric_label']='Subset macro'
    rows['oolong'].update(include_in_provisional_external_summary=False, reporting_status='scoring_mismatch',
        current_selected_system_description='EnSI-RAG, selected reference score71.84; GPT-4.1-mini/GPT-4.1.',
        caveat='Completed192-question labels-off, in-prompt test-split rerun at context length262144 (first192 in dataset order), score73.44. This replaces the incompatible labels-on staged-file99.00. EnSI-RAG71.84 uses an LLM soft judge for nonnumeric answers, while this Codex run uses the official exact/substring scorer. The Codex result is retained; the aggregate paper comparison remains pending aligned regrading or a numeric-only join. Fractional credit makes a binomial interval inappropriate.')
    rows['crag']['metric']='truthfulness = accuracy - hallucination; all578 native grades'
    rows['crag']['interval_description']='No binary interval: signed composite over578 grades (435correct,106hallucinations,37missing).'
    rows['rarebench']['interval_description']='No interval for the pending primary result; the old interval is retained only in previous_measurement.'
    rows['chembench']['validation_pending']=['Gold-source trajectory-scan artifact has not yet been verified in this paper refresh.']
    rows['chembench']['caveat'] += ' Gold-source trajectory-scan verification remains pending in this working draft.'
    for row in rows.values():
        for key in ['current_reference','figure_published_reference']:
            if row.get(key):
                row[key].pop('gap',None)
                row[key].pop('gap_se',None)
        row['caveat']=re.sub(r',(?=\S)', ', ', row['caveat'])
        row['caveat']=re.sub(r'\s*=\s*', ' = ', row['caveat'])
        row['caveat']=re.sub(r'(?<=[A-Za-z])(?=[0-9])|(?<=[0-9])(?=[A-Za-z])',' ',row['caveat'])
    # Suite membership is fixed independently of which new HF results are found.
    suite = json.loads(SUITE.read_text())
    suite_ids = suite['benchmark_ids']
    assert len(suite_ids)==len(set(suite_ids))==suite['study_benchmark_count']==20
    assert set(suite_ids) <= rows.keys()
    main_rows = [r for r in rows.values() if r['slug'] in suite_ids]
    supplementary_rows = [r for r in rows.values() if r['slug'] not in suite_ids]
    for row in main_rows: row['study_membership']='main'
    for row in supplementary_rows:
        row['study_membership']='supplementary'
        row['membership_note']=suite['replacement']['reason']
        row['supplementary_reference_comparable']=row['include_in_provisional_external_summary']
        row['include_in_provisional_external_summary']=False
    data['rows']=main_rows
    data['supplementary_rows']=supplementary_rows
    comparable=[r for r in data['rows'] if r['include_in_provisional_external_summary']]
    relations={'higher':0,'lower':0,'equal':0}
    for r in comparable:
        difference=r['score']-r['figure_published_reference']['score']
        relations['higher' if difference>0 else 'lower' if difference<0 else 'equal']+=1
    data.update(schema_version=3,measurement_snapshot_date='2026-09-18',original_dashboard_date='2026-09-09',
        hf_refresh_source=str(UPDATE.relative_to(ROOT)),hf_refs_source='data/hf_refresh/refs.json',
        study_suite_source=str(SUITE.relative_to(ROOT)),
        study_benchmarks=len(main_rows),initial_study_benchmarks=20,
        supplementary_benchmarks=len(supplementary_rows),total_archived_benchmark_records=len(rows),
        retained_codex_measurements=sum(r['valid_codex_measurement'] for r in main_rows),
        primary_or_scoped_measurements=sum(r['codex_role']=='primary' for r in main_rows),
        scored_variants=sum(r['codex_role']=='variant' for r in main_rows),
        provisional_external_point_comparisons={'n':len(comparable),**relations,
            'suite_denominator':len(main_rows),'unclassified':len(main_rows)-len(comparable),
            'warning':'Descriptive selected-paper point comparison only. Includes the declared ChemBench150-question pilot; excludes scored variants, unmatched aggregate references, and the OOLONG scorer mismatch. No statistical win/loss/parity classification.'})
    (ROOT/'data/results_snapshot.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    with (ROOT/'data/results_snapshot.csv').open('w',newline='') as f:
        cols=['slug','study_membership','score','n_measured','metric','codex_role','reporting_status','valid_codex_measurement','include_in_provisional_external_summary','paired_comparator_complete','paper_score','caveat']
        writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader()
        for row in main_rows + supplementary_rows:
            item={k:row.get(k) for k in cols};item['paper_score']=(row.get('figure_published_reference') or {}).get('score');writer.writerow(item)
    print(json.dumps({k:data[k] for k in ['study_benchmarks','retained_codex_measurements','primary_or_scoped_measurements','scored_variants','provisional_external_point_comparisons']}))

if __name__=='__main__': main()
