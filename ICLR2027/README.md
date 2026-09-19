# Working paper — HF refresh, 2026-09-18

Open `main.tex` or the compiled `main.pdf`.

The manuscript files (`1_abstract.tex` through `10_result_details.tex`) live alongside `main.tex`. `main.tex` includes them in reading order; figures, data, and generation scripts remain in their respective directories.

- Figure1 covers the 20-benchmark suite, including updated Codex scores, explicit subsets and protocol variants. SSTQA replaces LongBench v2; the earlier LongBench result is retained in the supplementary results.
- Figure2 is a vector diagram with selection review checkpoints, audit stages, two comparison paths, and evidence/review layer. The first stage labels evidence screening, feasibility review, and study inclusion; the method table explains their conditions. Historical counts are not execution-readiness statuses or a frozen nested selection ledger. Editable source: `scripts/build_audit_pipeline.py`; PDF, SVG, and PNG are in `figures/`.
- Abstract, experiments, full score table, and ELAIPBench paired statistics use the refreshed snapshot.
- Related Work and the method/appendix citations now resolve to 23 verified literature or software references. Primary-source metadata and claim mappings are recorded in `data/reference_verification_related.md` and `data/reference_verification_method.md`.
- Experiments follows the current abstract's three analysis questions: workflow stages and accuracy, information preservation across decomposition, and domain conventions/conditions/verification. Selected FinanceMath and IndustryOR trace cases, source hashes, and the limits of each inference are recorded in `data/experiment_claim_evidence.md`.

The main suite contains **20 benchmarks and 19 retained scores** (13 primary/scoped settings plus 6 labelled variants). The **11 descriptive paper comparisons** contain 7 higher and 4 lower point estimates. Using the full suite as the denominator gives 7/20 (35%) higher, 4/20 (20%) lower, and 9/20 (45%) unclassified. The registration abstract uses the draft wording "outperforms / underperforms / performs on par" with 35%, 20%, and 45% displayed without TODO markup; final validation remains pending; the underlying statistics retain the unclassified status for the last group. These are not statistical win/loss/parity rates. MedAgentsBench lacks a matching paper aggregate, OOLONG needs scorer-aligned regrading, and six variants retain their actual protocol labels. SSTQA's 77.23 is the English-split judge variant; its Chinese-split primary result is pending. RareBench still needs a valid network-enabled rerun. Comparator completion is tracked independently.

The snapshot also preserves LongBench v2 as a supplementary measurement outside the main suite and its aggregate counts. The comparator roster records SSTQA taking the LongBench slot because DeLM's LongBench-v2 implementation is unreleased (`4_comparators/FULL_RUN_ESTIMATES.md`, line 17, in the source evaluation repository).

## Regenerate from the included snapshot

From this directory:

```bash
python3 scripts/build_paper_results.py
python3 scripts/build_audit_pipeline.py
python3 scripts/paired_results.py --replay data/paired_results.json --output /tmp/paired_results_recomputed.json
/tmp/iclr2027-tex-bin/tectonic --only-cached --keep-logs main.tex
```

Figures require Matplotlib; statistical replay requires NumPy. These commands make no API calls. `fonts.tex` supports Times under pdfLaTeX and TeX Gyre Termes under XeLaTeX/Tectonic.

The verified HF update and source hashes are in `data/hf_refresh/`. `data/results_snapshot.json` is the current integrated source; `data/paired_results.json` contains703 paired outcomes. See `data/README.md` for reporting categories and refresh details. Updating the data is separate from rendering; `scripts/refresh_results_snapshot.py` requires the local source evaluation files for extraction and verification.

Unfinished comparator results, aligned regrading, trace interventions, and verification checks remain `\todo{...}`. Citation placeholders have been replaced with verified entries; full benchmark-source manifests and the unfinished empirical checks still need to be frozen before submission.

The draft before this HF refresh is preserved at `/tmp/iclr2027_paper_before_hf_refresh_20260918`; the prior raw result snapshot is also archived under `data/history/`.
