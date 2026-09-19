#!/usr/bin/env python3
"""Freeze the measured dashboard scores and subsequent local audit decisions.

No models are called. Historical scores are not silently promoted to results under
a changed protocol. Re-running this script requires the two local source paths.
"""
import csv
import hashlib
import html
import json
import re
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1]
DASHBOARD = Path('/home/jiacheng/RESULTS_DASHBOARD (1).html')
REPO = Path('/data1/jiacheng/multiagent_repo_analysis/codex-generalization')
SPECS = REPO / '3_deploy_run/quickstart/scenario1_specs'


def clean(value):
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', '', value)).split())


def span(body, cls):
    match = re.search(r'<span class="' + cls + r'">(.*?)</span>', body, re.S)
    return clean(match.group(1)) if match else None


DOMAINS = {
    'stark': 'Knowledge-graph retrieval', 'bright': 'Reasoning-intensive retrieval',
    'scitab': 'Scientific fact verification', 'llm_srbench': 'Symbolic regression',
    'industryor': 'Operations research', 'financemath': 'Financial mathematics',
    'longbench_v2': 'Long-context question answering', 'multihiertt': 'Financial table reasoning',
    'earthbench': 'Earth science', 'insightbench': 'Exploratory data analysis',
    'test_of_time': 'Temporal reasoning', 'elaipbench': 'Scientific paper understanding',
    'biomni_eval1': 'Biomedicine', 'matscibench': 'Materials science',
    'chembench': 'Chemistry', 'crag': 'Retrieval-augmented question answering',
    'medagentsbench': 'Medical reasoning', 'frontierscience_research': 'Scientific research',
    'oolong': 'Long-context aggregation', 'rarebench': 'Rare-disease diagnosis',
}

# Current names and scores are drawn from run_policy.json and the dated decisions
# cited below. OOLONG's stale top-level sota_score is overridden by its explicit
# comparator_change_2026_09_10 and sota_score_alternatives.ensi_rag fields.
CURRENT_REFS = {
    'stark': ('ARK', 'GPT-4.1', 48.2),
    'bright': ('RARG', 'GPT-5.4-mini', 51.75),
    'insightbench': ('DataSTORM', 'gpt-5-2025-08-07', 61.9),
    'test_of_time': ('REMem-I', 'GPT-4.1-mini-2025-04-14', 93.1),
    'frontierscience_research': ('FrontierAgent (Agent Team)', 'Apodex 1.1 (unreleased weights)', 63.3),
    'oolong': ('EnSI-RAG', 'GPT-4.1-mini / GPT-4.1', 71.84),
}

STATUS = {
    'stark': ('baseline_snapshot', 'Current selected reference is ARK (48.2), replacing AF-Retriever (46.2). Eight of 2,801 emitted trials excluded by the recorded measurement rule; seven have no grade. Tool asymmetry and published-backbone difference remain.'),
    'bright': ('baseline_snapshot', 'Current executable comparator is RARG (51.75), replacing RARG+ (53.36); the RARG+ entry-point implementation was not released. Published sampling protocol is unstated.'),
    'scitab': ('baseline_snapshot', 'Published result uses optimized prompts; no same-backbone completed comparator result in this score snapshot.'),
    'llm_srbench': ('baseline_snapshot', 'Dashboard uses 116/127 measured instances; registered denominator is 129 (116/129=89.92). Both must remain visible.'),
    'industryor': ('baseline_snapshot', '73.0 is on the original paper answer key; revised-key score is 80.0 and must not be compared to the original 68.0 bar.'),
    'financemath': ('baseline_snapshot', 'Published-backbone comparison; a separate completed same-backbone reproduction is available.'),
    'longbench_v2': ('baseline_snapshot', 'Five-domain macro on 125 Multi-Doc QA rows; paper bar is a mean over three runs, with no released benchmark driver.'),
    'multihiertt': ('baseline_snapshot', '744/1042 measured, versus 1044 emitted; same metric is answer accuracy, not the benchmark F1 column.'),
    'earthbench': ('baseline_snapshot', '162/247 reproduces 65.59 from released reference outputs; camera-ready 65.99 conflicts with those outputs. Gold-version and modality findings require separate analysis; historical verdict used a 3-SE threshold.'),
    'insightbench': ('restricted_variant', 'Old closed-web run and different judge; current DataSTORM bar corrected to 61.9. Sept17 open-web rerun has 35 recorded errors and an all-zero job summary, so no replacement score is promoted.'),
    'test_of_time': ('baseline_snapshot', '280 balanced instances of a 2800-instance population. Current paper bar is 93.1, not the unsupported 99.0 prose value. Format-instruction ablation 274/280 is an ablation; original 248/280 is not post-corrected.'),
    'elaipbench': ('baseline_snapshot', '151/399 measured of 403 emitted. Published AgentSPEX used high effort; Codex used medium. Updated medium-effort comparator must be reported separately.'),
    'biomni_eval1': ('restricted_variant', 'Historical arm lacked the benchmark Biomni E1 environment/data lake. Current baseline repair and comparator run are separate pending work.'),
    'matscibench': ('restricted_variant', 'Sept18 policy records all 1025 historical prompts on a retired 15-host restricted surface. Neither the later closed prompt nor the newly selected open-web surface produced this score.'),
    'chembench': ('restricted_variant', 'Historical full run was closed-web; benchmark baseline permits tools/web. Sept15 open-web pilot is 113/150=75.33, not a replacement full-suite result.'),
    'crag': ('restricted_variant', 'Historical input was pre-retrieved KG material rather than the benchmark mock API, and judge differs. Historical 0.3893 reference is a local regrade of released outputs, not the paper score.'),
    'medagentsbench': ('no_comparable_reference', 'GSEM publishes no nine-subset macro corresponding to this row; no aggregate reference is manufactured from the five published subsets.'),
    'frontierscience_research': ('restricted_variant', 'Historical closed-book score; current reference is open-book FrontierAgent63.3. EoM8.5 is ineligible because of threshold/split/training overlap differences.'),
    'oolong': ('invalid_for_current_comparison', 'Historical labels-on staged-file100 score; current selected setting is labels-off in-prompt test192. EnSI-RAG71.84 cannot be subtracted from the old99.0.'),
    'rarebench': ('invalid_measurement', 'Historical370-run retrieval failed on every network attempt; no comparison against retrieval-enabled DeepRare is admissible.'),
}


def main():
    raw = DASHBOARD.read_text()
    rows = []
    for html_slug, body in re.findall(r'<details class="bm" id="bm-([^"\n]+)">(.*?)</details>', raw, re.S):
        slug = 'frontierscience_research' if html_slug == 'frontierscience' else html_slug
        summary = re.search(r'<summary>(.*?)</summary>', body, re.S).group(1)
        meta = span(summary, 'meta')
        ci_text = span(summary, 'ci')
        ci_match = re.search(r'\[([\d.]+), ([\d.]+)\]', ci_text or '')
        se_match = re.search(r'SE ([\d.]+)', ci_text or '')
        refs = []
        for table in re.findall(r'<table class="rt">(.*?)</table>', body, re.S):
            if '<th>reference</th>' not in table:
                continue
            for tr in re.findall(r'<tr>(.*?)</tr>', table, re.S)[1:]:
                cells = [clean(c) for c in re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)]
                refs.append(dict(zip(['system', 'backbone', 'paper', 'score', 'gap', 'gap_se', 'sampling'], cells)))
            for ref in refs:
                ref['score'] = float(ref['score'])
                ref['backbone'] = ref['backbone'].replace('†', '')
        policy_path = SPECS / slug / 'run_policy.json'
        policy = json.loads(policy_path.read_text())
        current_ref = dict(refs[0]) if refs else None
        if slug in CURRENT_REFS:
            system, backbone, score = CURRENT_REFS[slug]
            current_ref = {'system': system, 'backbone': backbone, 'score': score}
        published_ref = dict(current_ref) if current_ref else None
        if slug == 'earthbench':
            published_ref.update(score=65.99,
                paper='Earth-Agent, arXiv:2509.23141v3 Table 1',
                provenance='Camera-ready paper cell. Versions 1/2 and released predictions give65.59; v3 appendix modality cells still reconstruct65.59.',
                source=str(policy_path) + ':sota_system')
        elif slug == 'crag':
            published_ref.update(score=0.711,
                paper='CacheRAG, arXiv:2604.26176v4 Table 1',
                provenance='Paper truthfulness=0.711; accuracy0.824/hallucination0.112/missing0.064. Registered0.3893 is a local regrade of released predictions under a different judge, not a paper score.',
                source=str(policy_path) + ':sota_system')
        elif published_ref:
            published_ref['source'] = str(policy_path)
            published_ref['provenance'] = 'Selected published reference; may differ from the strongest unreproducible system.'
        status, caveat = STATUS[slug]
        score = float(span(summary, 'score'))
        rows.append({
            'slug': slug, 'name': span(summary, 'bname'), 'domain': DOMAINS[slug],
            'score': score, 'n_measured': int(re.search(r'n=(\d+)', meta).group(1)),
            'metric': meta.split(' · ', 1)[1], 'scale': [-1, 1] if slug == 'crag' else [0, 100],
            'ci95': [float(v) for v in ci_match.groups()] if ci_match else None,
            'se': float(se_match.group(1)) if se_match else None,
            'interval_description': clean(re.search(r'<p class="cim">(.*?)</p>', body, re.S).group(1)) if '<p class="cim">' in body else ci_text,
            'historical_verdict': clean(re.search(r'<span class="pill[^"\n]*">(.*?)</span>', summary, re.S).group(1)),
            'historical_references': refs, 'current_reference': current_ref,
            'figure_published_reference': published_ref,
            'current_selected_system_description': policy.get('sota_system'),
            'reporting_status': status, 'caveat': caveat,
            'include_in_provisional_external_summary': status == 'baseline_snapshot',
            'policy_source': str(policy_path),
            'policy_sha256': hashlib.sha256(policy_path.read_bytes()).hexdigest(),
            'dashboard_anchor': 'bm-' + html_slug,
        })
    assert len(rows) == 20
    # Point-estimate relations are descriptive. A tie here would be exact numeric
    # equality, not evidence for statistical equivalence.
    eligible = [r for r in rows if r['include_in_provisional_external_summary']]
    relations = {'higher': 0, 'lower': 0, 'equal': 0}
    for row in eligible:
        gap = row['score'] - row['current_reference']['score']
        relations['higher' if gap > 0 else 'lower' if gap < 0 else 'equal'] += 1
    data = {
        'schema_version': 1,
        'measurement_snapshot_date': '2026-09-09',
        'audit_overlay_date': '2026-09-18',
        'dashboard_source': str(DASHBOARD),
        'dashboard_sha256': hashlib.sha256(DASHBOARD.read_bytes()).hexdigest(),
        'audit_sources': [str(REPO / p) for p in ['experiment_design.md', '3_deploy_run/RERUNS.md', '4_comparators/DECISIONS.md']],
        'audited_candidates': len(list(csv.DictReader((REPO / '1_collection/benchmark_audit_full.csv').open()))),
        'ready_candidates': len(json.loads((REPO / '1_collection/ready_manifest.json').read_text())),
        'completed_historical_score_rows': len(rows),
        'provisional_external_point_comparisons': {'n': len(eligible), **relations,
            'warning': 'Descriptive relation to published point estimates only; not win/loss/par, no equivalence test, and not same-backbone attribution. Historical scores with current selected references; pending protocol repairs are omitted.'},
        'rows': rows,
    }
    out = PAPER / 'data'
    out.mkdir(exist_ok=True)
    (out / 'historical_dashboard_snapshot.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    with (out / 'historical_dashboard_snapshot.csv').open('w', newline='') as handle:
        names = ['slug', 'name', 'domain', 'score', 'n_measured', 'metric', 'ci95', 'se', 'historical_verdict', 'current_reference_system', 'current_reference_score', 'current_reference_backbone', 'reporting_status', 'caveat']
        writer = csv.DictWriter(handle, fieldnames=names)
        writer.writeheader()
        for row in rows:
            item = {k: row.get(k) for k in names}
            ref = row['current_reference'] or {}
            for k in ['system', 'score', 'backbone']:
                item['current_reference_' + k] = ref.get(k)
            writer.writerow(item)
    print(json.dumps({k: v for k, v in data.items() if k != 'rows'}, indent=2))


if __name__ == '__main__':
    main()
