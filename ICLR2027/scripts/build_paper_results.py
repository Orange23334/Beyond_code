#!/usr/bin/env python3
"""Build Figure 1 and the score/provenance appendix from the frozen local snapshot.

No inference calls or network requests. Run from any directory with Python and
matplotlib. Extracting a new snapshot is a separate, explicit operation.
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'data/results_snapshot.json').read_text())
ROWS = {r['slug']: r for r in DATA['rows']}
SUPPLEMENTARY = DATA.get('supplementary_rows', [])
GROUPS = [
    ('Retrieval and long context', ['stark', 'bright', 'sstqa', 'crag', 'oolong']),
    ('Scientific reasoning', ['scitab', 'llm_srbench', 'earthbench', 'matscibench', 'chembench', 'frontierscience_research', 'elaipbench']),
    ('Clinical and biomedical', ['biomni_eval1', 'medagentsbench', 'rarebench']),
    ('Quantitative and data tasks', ['industryor', 'financemath', 'multihiertt', 'insightbench']),
    ('Temporal reasoning', ['test_of_time']),
]
METRICS = {
    'sstqa': 'Judge accuracy', 'stark': 'Hit@1', 'bright': 'nDCG@10', 'crag': 'Truthfulness',
    'financemath': 'Accuracy', 'industryor': 'Accuracy', 'multihiertt': 'Answer acc.',
    'insightbench': 'Insight score', 'elaipbench': 'Accuracy', 'scitab': 'Accuracy',
    'test_of_time': 'Accuracy', 'longbench_v2': 'Macro acc.', 'oolong': 'Official score',
    'llm_srbench': 'Acc. at 0.1', 'earthbench': 'Answer acc.', 'chembench': 'Overall score',
    'matscibench': 'Text accuracy', 'frontierscience_research': 'Rubric pass rate',
    'biomni_eval1': 'Branch macro', 'medagentsbench': 'Subset macro', 'rarebench': 'Recall@1',
}
STATUS = {'baseline_snapshot': '', 'updated_baseline': '', 'planned_subset': 'S',
          'scored_variant': 'V', 'scoring_mismatch': 'J', 'awaiting_validation': 'P', 'restricted_variant': 'R',
          'invalid_for_current_comparison': 'I', 'invalid_measurement': 'I',
          'no_comparable_reference': 'N'}


def tex(s):
    replacements = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
                    '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
                    '−': '-', '≥': r'$\geq$', '≤': r'$\leq$'}
    return ''.join(replacements.get(c, c) for c in str(s))


def paper_ref(row):
    return row.get('figure_published_reference', row['current_reference'])


def valid_codex(row):
    return row.get('valid_codex_measurement', row['reporting_status'] in
                   {'baseline_snapshot', 'updated_baseline', 'planned_subset', 'no_comparable_reference'})


def score_string(value, slug):
    if value is None:
        return '--'
    return f'{value:.4f}' if slug == 'crag' else f'{value:.2f}'


def main():
    assert {slug for _, slugs in GROUPS for slug in slugs} == set(ROWS)
    assert len(ROWS) == DATA['study_benchmarks'] == 20
    comparable = [r for r in DATA['rows'] if r['include_in_provisional_external_summary']]
    summary = {k: 0 for k in ['higher', 'lower', 'equal']}
    for row in comparable:
        difference = row['score'] - paper_ref(row)['score']
        summary['higher' if difference > 0 else 'lower' if difference < 0 else 'equal'] += 1
    ncomp, nvalid, ntotal = len(comparable), sum(valid_codex(r) for r in DATA['rows']), len(DATA['rows'])
    macros = {'StudyBenchmarkCount': ntotal, 'RetainedCodexCount': nvalid,
              'PrimaryCodexCount': sum(r.get('codex_role')=='primary' for r in DATA['rows']),
              'VariantCodexCount': sum(r.get('codex_role')=='variant' for r in DATA['rows']), 'PaperComparisonCount': ncomp,
              'PaperHigherCount': summary['higher'], 'PaperLowerCount': summary['lower'],
              'PaperEqualCount': summary['equal'],
              'PaperUnclassifiedCount': ntotal-ncomp,
              'SuiteHigherPercent': f"{100*summary['higher']/ntotal:.1f}",
              'SuiteLowerPercent': f"{100*summary['lower']/ntotal:.1f}",
              'SuiteUnclassifiedPercent': f"{100*(ntotal-ncomp)/ntotal:.1f}",
              'PaperHigherPercent': f"{100*summary['higher']/ncomp:.1f}",
              'PaperLowerPercent': f"{100*summary['lower']/ncomp:.1f}"}
    (ROOT / 'data/result_summary.tex').write_text('% Generated from results_snapshot.json; do not hand-edit.\n' +
        ''.join('\\newcommand{\\' + name + '}{' + str(value) + '}\n' for name, value in macros.items()))
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                         'pdf.fonttype': 42, 'ps.fonttype': 42})
    fig, ax = plt.subplots(figsize=(8.6, 7.35))
    fig.subplots_adjust(left=.28, right=.775, top=.91, bottom=.095)
    blue, orange, muted = '#1764ab', '#be650b', '#858b92'
    y = 0
    positions, boundaries = [], []
    for group, slugs in GROUPS:
        y += .72
        boundaries.append((y-.58, group))
        for slug in slugs:
            positions.append((y, ROWS[slug]))
            y += 1
    for k, (pos, row) in enumerate(positions):
        eligible = row['include_in_provisional_external_summary']
        current = valid_codex(row)
        if not current:
            ax.axhspan(pos-.42, pos+.42, color='#f1f2f4', zorder=0)
        factor = 100 if row['slug'] == 'crag' else 1
        score = None if row['score'] is None else row['score'] * factor
        ref = paper_ref(row)
        reference = None if ref is None else ref['score'] * factor
        if eligible and reference is not None:
            ax.plot([score, reference], [pos, pos], color='#b5bcc4', lw=1.1, zorder=1)
        if row['ci95']:
            lo, hi = [v * factor for v in row['ci95']]
            ax.plot([lo, hi], [pos, pos], color=blue if current else muted,
                    lw=.9, alpha=1 if current else .6, zorder=2)
        if score is not None:
            variant = row.get('codex_role') == 'variant'
            ax.plot(score, pos, 'o', color=blue if current else muted,
                    markerfacecolor=blue if current and not variant else 'white', markersize=4.7, zorder=4)
        if reference is not None:
            ax.plot(reference, pos, 'D', markerfacecolor='white',
                    markeredgecolor=orange if eligible else muted, markersize=4.3, zorder=3)
        tag = STATUS[row['reporting_status']]
        label = ('BRIGHT' if row['slug']=='bright' else row['name']) + (f'  [{tag}]' if tag else '')
        ax.text(-.055, pos, label, transform=ax.get_yaxis_transform(), ha='right', va='center',
                fontsize=9, color='#24292f' if current else '#626a73')
        numbers = score_string(row['score'], row['slug']) + ' / ' + score_string(None if ref is None else ref['score'], row['slug'])
        ax.text(1.035, pos, numbers, transform=ax.get_yaxis_transform(), va='center', fontsize=8.5,
                color='#24292f' if current else '#626a73')
    for pos, group in boundaries:
        ax.text(-.55, pos, group, transform=ax.get_yaxis_transform(), ha='left', va='bottom',
                fontsize=9, fontweight='bold', color='#333b44')
    ax.text(1.035, -.15, 'Codex / Paper', transform=ax.get_yaxis_transform(), fontweight='bold', fontsize=8)
    ax.set_xlim(-1, 102)
    ax.set_ylim(y-.15, -1.2)
    ax.set_yticks([])
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel('Benchmark score (CRAG truthfulness × 100 for display)', fontsize=8.5)
    ax.grid(axis='x', color='#e6e9ed', linewidth=.6, zorder=0)
    for side in ['left', 'right', 'top']:
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#c3c8ce')
    handles = [Line2D([0], [0], marker='o', linestyle='none', color=blue, label='Codex: primary / scoped subset'),
               Line2D([0], [0], marker='D', linestyle='none', markerfacecolor='white', color=orange, label='Selected published reference'),
               Line2D([0], [0], marker='o', linestyle='none', markerfacecolor='white', color=blue, label='Codex: specified variant')]
    fig.legend(handles=handles, loc='upper center', ncol=3, frameon=False, fontsize=8,
               bbox_to_anchor=(.49, .995), columnspacing=1.4)
    fig.text(.025, .033, 'Compare scores within a row. Lines: recorded Codex 95% intervals where available.', fontsize=7.5)
    fig.text(.025, .013, '[S] subset  [V] variant  [J] scorer mismatch  [I/P] score pending  [N] no paper aggregate', fontsize=7.5)
    (ROOT / 'figures').mkdir(exist_ok=True)
    fig.savefig(ROOT / 'figures/direct_codex_vs_published.pdf')
    fig.savefig(ROOT / 'figures/direct_codex_vs_published.png', dpi=180)
    plt.close(fig)

    out = [r'\section{Per-benchmark scores and reporting status}', r'\label{app:result-details}',
        r'Table~\ref{tab:all-results} records the selected direct-Codex measurements after checking',
        r'the updated Hugging Face results and local source artifacts on',
        r'2026-09-18. Run-level provenance distinguishes reruns, planned subsets, and earlier',
        r'variants. A completed Codex result does not require a completed comparator run.',
        r'Figure~\ref{fig:main-results} uses paper scores; locally regraded reference outputs are',
        r'distinguished in the notes below. The comparator campaign remains in progress.',
        r'CRAG retains its native signed truthfulness scale in the table and is multiplied by 100',
        r'only for display in the figure. All other scores are on a 0--100 scale.',
        r'The main suite has 20 benchmarks: SSTQA replaces LongBench-v2, whose measurement is',
        r'preserved as supplementary evidence below. Suite membership is frozen separately from',
        r'result availability in \texttt{data/study\_suite.json}.',
        r'The reference is the selected comparison system, which need not be the highest reported',
        r'system when that system cannot be executed (e.g., RARG versus RARG+).', '',
        r'\begingroup', r'\scriptsize', r'\setlength{\tabcolsep}{3pt}',
        r'\begin{longtable}{@{}p{.20\textwidth}p{.16\textwidth}rrrp{.22\textwidth}@{}}',
        r'\caption{Selected Codex scores and published references. S: planned subset; R/V: variant;',
        r'J: scorer mismatch; I/P: pending primary score; N: no matching published aggregate.',
        r'Codex-result validity and inclusion in the published-score summary are separate, with the per-row',
        r'qualifications below. $n$ is the reported evaluation denominator; scheduled versus graded',
        r'coverage is specified per row.}',
        r'\label{tab:all-results}\\',r'\toprule',
        r'Benchmark & Metric & $n$ & Codex & Paper & Reference system \\',r'\midrule',r'\endfirsthead',
        r'\toprule',r'Benchmark & Metric & $n$ & Codex & Paper & Reference system \\',r'\midrule',r'\endhead',
        r'\bottomrule',r'\endfoot']
    for _, slugs in GROUPS:
        for slug in slugs:
            row = ROWS[slug]; ref=paper_ref(row); tag=STATUS[row['reporting_status']]
            name = row['name'] + (' [' + tag + ']' if tag else '')
            vals = [tex(name),tex(row.get('metric_label', METRICS[slug])),str(row['n_measured']),score_string(row['score'],slug),
                    score_string(None if ref is None else ref['score'],slug),tex(ref['system']) if ref else '--']
            out.append(' & '.join(vals)+r' \\')
    out += [r'\end{longtable}',r'\endgroup','',r'\paragraph{Interpretation of the aggregate.}',
        f'{nvalid} of {ntotal} benchmarks have retained Codex measurements: '
        f"{DATA.get('primary_or_scoped_measurements', nvalid)} primary/scoped results and "
        f"{DATA.get('scored_variants', 0)} specified protocol variants.",
        f'{ncomp} settings enter the descriptive published-score count: '
        f'{summary["higher"]}/{ncomp} ({100*summary["higher"]/ncomp:.1f}\\%) higher, '
        f'{summary["lower"]}/{ncomp} ({100*summary["lower"]/ncomp:.1f}\\%) lower, '
        f'and {summary["equal"]} exactly equal.',
        f'Using all {ntotal} study benchmarks as the denominator gives '
        f'{summary["higher"]}/{ntotal} ({100*summary["higher"]/ntotal:.1f}\\%) higher, '
        f'{summary["lower"]}/{ntotal} ({100*summary["lower"]/ntotal:.1f}\\%) lower, and '
        f'{ntotal-ncomp}/{ntotal} ({100*(ntotal-ncomp)/ntotal:.1f}\\%) not yet classified.',
        r'This is not a significance or equivalence classification. A missing compatible paper',
        r'aggregate, unfinished judging, or an unfinished comparator does not automatically',
        r'invalidate an independently scored Codex measurement; the relevant status is recorded',
        r'separately. Only comparison-eligible rows contribute to the external tally.',
        r'Even retained rows can differ in published backbone, sampling protocol, and measured',
        r'denominator; no pooled performance or population-level win rate is estimated.', '',
        r'\paragraph{Per-row provenance and qualifications.}']
    for _, slugs in GROUPS:
        for slug in slugs:
            row=ROWS[slug]; ref=paper_ref(row)
            source = '' if ref is None else ' Reference backbone: '+ref['backbone']+'.'
            note = row['caveat'] + source
            provenance = row.get('measurement_provenance', {})
            if provenance.get('sources') or provenance.get('run_id'):
                note += ' Selected run: ' + provenance.get('run_id', provenance.get('branch', 'recorded in snapshot')) + '.'
                if provenance.get('branch'): note += ' HF branch: ' + provenance['branch'] + '.'
                if provenance.get('commit'): note += ' Revision: ' + provenance['commit'][:12] + '.'
            if slug=='bright': note += ' The higher reported RARG+ score is 53.36, versus the selected executable RARG score of 51.75.'
            if slug=='earthbench': note += ' Figure 1 and the table show the paper value 65.99; the locally reconstructed 65.59 remains an audit discrepancy, not a silent correction to the paper. A separate same-key regrade on 246 records gives Codex 59.35 versus released-output 65.04; restricting to 218 agreeing answer keys gives 65.60 versus 70.64. These are sensitivity comparisons, not the paper table cell.'
            if slug=='crag': note += ' Figure 1 shows the paper truthfulness 0.711, not the locally regraded 0.3893; no direct gap is interpreted.'
            out.append(r'\paragraph{'+tex(row['name'])+r'.} '+tex(note))
    if SUPPLEMENTARY:
        out += ['', r'\subsection{Supplementary measurements outside the main suite}',
                r'\label{app:supplementary-results}',
                r'These measurements are preserved for reference and do not change the 20-benchmark',
                r'study denominator, Figure~\ref{fig:main-results}, or the abstract counts.']
        for row in SUPPLEMENTARY:
            ref=paper_ref(row)
            note=(row.get('membership_note','')+' Codex '+score_string(row['score'],row['slug'])+
                  ' on '+str(row['n_measured'])+' instances; published reference '+
                  score_string(None if ref is None else ref['score'],row['slug'])+
                  (' ('+ref['system']+')' if ref else '')+'. '+row['caveat'])
            out.append(r'\paragraph{'+tex(row['name'])+r'.} '+tex(note))
    out += ['',r'\paragraph{Machine-readable provenance.}',
        r'\texttt{data/results\_snapshot.json} records source paths, SHA-256 hashes, metric',
        r'descriptions, intervals, reference metadata, and inclusion decisions.',
        r'\texttt{scripts/build\_paper\_results.py} regenerates this appendix and Figure~\ref{fig:main-results}',
        r'from that frozen file. Extraction from the source repository is a separate operation:',
        r'\texttt{scripts/refresh\_results\_snapshot.py} merges the verified HF update while',
        r'preserving the previous snapshot. The historical dashboard extractor writes only the',
        r'historical snapshot and cannot overwrite the current result file.',
        r'\todo{Freeze the final benchmark source manifest before submission.}', '',
        r'Paired outcomes and inference settings are exported in \texttt{data/paired\_results.json};',
        r'\texttt{scripts/paired\_results.py --replay data/paired\_results.json} recomputes the',
        r'statistics without the original run directories. The bounded trace observations in',
        r'Section~\ref{sec:analysis} are recorded with source hashes and case identifiers in',
        r'\texttt{data/trace\_evidence.json}.']
    (ROOT / '10_result_details.tex').write_text('\n'.join(out)+'\n')
    print(f'Generated Figure 1, result appendix, and summary macros: {ntotal} benchmarks; {nvalid} retained Codex; {ncomp} paper comparisons; {summary}.')

if __name__ == '__main__':
    main()
