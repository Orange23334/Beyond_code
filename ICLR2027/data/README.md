# Updated result snapshot — 2026-09-18

`results_snapshot.json` / `.csv` now incorporate verified mentor HF reruns, recovered task IDs, and corrected benchmark aggregation. The earlier 20-row dashboard snapshot is preserved in `history/results_snapshot_before_hf_refresh.json`; it is no longer the current source of headline scores.

The main study suite contains **20 benchmarks**, with SSTQA replacing LongBench v2:

- **19 retained scores**: 13 primary/explicitly scoped settings and 6 labelled protocol variants.
- **11 descriptive paper comparisons**: 7 higher point estimates, 4 lower. The completed ChemBench 150-question pilot is included and labelled; excluding it gives 7 higher/3 lower over 10.
- **Full-suite counts**: 7/20 (35%) higher, 4/20 (20%) lower, and 9/20 (45%) unclassified. The registration abstract displays its provisional 35% / 20% / 45% outperforms / underperforms / on-par wording without TODO markup; final validation remains pending; this does not change the source classification to on par.
- **3 completed paired comparator comparisons**, containing703 paired outcomes.
- RareBench's failed-network measurement remains diagnostic history; its primary `score` is `null`.

LongBench v2 remains in the snapshot and supplementary results, outside the main-suite counts. The replacement follows the source comparator roster (`4_comparators/FULL_RUN_ESTIMATES.md`, line 17): SSTQA takes the LongBench slot because DeLM's LongBench-v2 implementation is unreleased.

`study_suite.json` freezes the 20 main benchmark IDs and records the replacement source. In snapshot schema 3, `rows` contains those 20 main records and `supplementary_rows` preserves LongBench v2. The CSV includes both groups with an explicit `study_membership` column. All generated study counts and percentages use only the main rows; adding a newly discovered result cannot silently enlarge the study suite.

These are separate denominators. MedAgentsBench has a usable Codex macro score but no corresponding published aggregate. OOLONG's new 192-question score is retained; its paper comparison remains pending because EnSI-RAG uses a different nonnumeric scorer. The six scored variants are Biomni, MatSciBench, CRAG, InsightBench, FrontierScience, and SSTQA. SSTQA's 77.23 comes from the English split with a different judge; the Chinese-split primary evaluation is pending. Their measurements remain visible without being treated as measurements under the new target protocol.

## Provenance and refresh

`hf_refresh/refs.json` pins the34 remote branches observed during this refresh. `hf_refresh/selected_measurements.json` records native grades, aggregation, source commits, SHA256 hashes, and URLs for updated measurements. Local mirror result blobs were verified against HF metadata; new result/config files and selected verifier details were fetched directly. `hf_refresh/eligibility_audit.md` preserves the inclusion review and its final scoring-alignment correction.

`../scripts/refresh_results_snapshot.py` merges the verified update with the preserved earlier snapshot. It does not call models or network APIs. It checks source hashes and recomputes the CRAG denominator from local native verdicts, so the source evaluation repository must be mounted to rerun that extraction. `../scripts/extract_results_snapshot.py` now writes only historical dashboard files and cannot overwrite the current snapshot.

`../scripts/build_paper_results.py` regenerates Figure1, the detailed result appendix, and `result_summary.tex` from the included current JSON. Abstract/experiment percentages use these generated macros.

Reference fields remain distinct:

- `historical_references`: references from the old dashboard.
- `current_reference`: selected comparator/reference, including locally reconstructed values where recorded.
- `figure_published_reference`: actual paper value, e.g. CRAG0.711 and EarthBench65.99, rather than local regrades.

`valid_codex_measurement` means a retained scored result in its stated condition, including labelled variants; it does not certify all protocol checks or reference comparability. `codex_role`, `include_in_provisional_external_summary`, and `paired_comparator_complete` record those different questions. ChemBench's gold-source trajectory-scan verification remains TODO. Exact numeric equality and failure to reject a difference are not statistical equivalence.

`paired_results.json` includes all703 paired outcomes after ELAIPBench's four recovery trials replace its original failed executions. Run `../scripts/paired_results.py --replay paired_results.json --output /tmp/paired_replay.json` to recompute the statistics without original runs. `trace_evidence.json` records inspected cases and hashes.
