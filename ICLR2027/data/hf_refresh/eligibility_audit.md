> Final scoring-alignment review: retain OOLONG's new score, but its nonnumeric scorer differs from the EnSI-RAG paper. The final published-score tally is **12 (8 higher, 4 lower)**, not the initial 13 recommended below. Adding the newly uploaded SSTQA judge variant expands the reported inventory to **21 benchmarks, 20 retained scores: 14 primary/scoped + 6 variants**. The original all20 audit below is preserved as review history.

# Direct-Codex result eligibility audit (2026-09-18)

Previous `11` is NOT the number of measured Codex benchmarks. `scripts/extract_results_snapshot.py` hardcodes STATUS and includes only rows where `status == baseline_snapshot`. It used a Sept9 dashboard plus Sept18 audit overlay, and did not ingest newer HF reruns. A pending system comparator is not grounds for deleting an available direct-Codex score.

Recommended denominators after HF job checks: **19 usable measured Codex rows** (14 primary or explicitly scoped sample rows + 5 labelled historical variants), **13 descriptive paper-reference comparisons** (12 non-pilot settings plus ChemBench open-web n150 pilot with visible subset caveat), **1 invalid measurement** (RareBench dead-network run). **MedAgentsBench is a valid standalone primary result even though GSEM has no corresponding aggregate reference.** Paired comparator completion is a separate field and cannot be inferred from these counts. Neither13 nor19 is a count of statistically established wins/losses/parity.

## Governing owner rules

- `/data1/jiacheng/multiagent_repo_analysis/codex-generalization/4_comparators/DECISIONS.md:1238`: “direct codex要去跑benchmark的官方设定 … comparator要去复现S1的全套工具”. The surrounding entry explicitly supersedes same-surface parity: direct Codex runs the benchmark's official setting; comparator reproduces the system's full configuration. Their surfaces may differ and table must declare it.
- `DECISIONS.md:1772`: “打分要保证codex规则对齐，而codex是跟paper对齐，paper和repo没提的按官方benchmark对齐”. Score-rule precedence: comparator paper, then repo, then official benchmark metric. Both arms scored by that same rule.
- `DECISIONS.md:1264`: owner “multihiertt就用1044”; headline744/1044=71.26. The1042 dashboard denominator reconstructs from nothing.

## All20 recommendations

| Slug | Current measured number / coverage | Valid measurement? | Reporting class | Paper-reference summary? | Evidence and action |
|---|---|---|---|---|---|
| stark | Old2068/2793=74.04; newer7-trial backfill pending HF merge | Yes | primary | Yes | HF agent merging backup/stark_rerun7 into original2801 ids. Use its final deduplicated result, retain missing policy explicitly. |
| bright | Four-domain macro61.09, n423 | Yes | primary | Yes | Existing dashboard macro is correct instrument; native job micro61.30 is not the macro. RARG51.75 is selected executable reference, RARG+53.36 unreleased component. |
| scitab |892/1224=72.88 | Yes | primary | Yes | Full native run. Reference70.6. |
| llm_srbench |116/129=89.92 intended full set;116/127=91.34 conditional measured-only | Yes | primary | Yes | Native job result n129, reward116. Report full planned-set score as headline with two unmeasured trials visible; historical dashboard91.34 is conditional. No comparator result required. |
| industryor |73/100=73.00 | Yes | primary | Yes | Keep original answer-key result when comparing paper68.0. Revised-key80.0 is sensitivity result. |
| financemath |158/200=79.00 | Yes | primary | Yes | Full native result, paper76.0. |
| longbench_v2 |Five MultiDoc-subdomain macro61.54, n125; full run503 | Yes | scoped primary | Yes |61.54 is correct paper-reference slice/macro, not native full503 micro69.78. Reference60.1. |
| multihiertt |744/1044=71.2644 ->71.26 | Yes | primary | Yes | Owner explicitly corrected denominator1044; snapshot71.40/n1042 stale. |
| earthbench |Original full247 key1:146/247=59.11. Latest same-key audit246 scorableGT:59.35 | Yes | primary + scorer sensitivity | Yes with version/denominator caveat | Preserve original24759.11 for existing full-paper bar; latest DECISIONS1779+ describes246-pair key1 regrade59.35 vs releasedEarthAgent65.04, a separate paired regrade. Paper v3 bar65.99, v1/v2/released162/24765.59. Do not relabel65.04 as paper score. |
| test_of_time |248/280=88.57 | Yes | primary | Yes | New arm2=274/28097.86 is prompt-format ablation, NOT replacement primary; owner DECISIONS1360+. Paper93.1, not99.0. |
| elaipbench |Old151/399=37.84;4-trial Sept15 backfill pending HF merge | Yes | primary | Yes | HF agent merging backup/elaipbench_rerun4 into planned403. High-effort published bar versus medium Codex disclosed. |
| oolong |73.4413167001, n192,0 errors | Yes | refreshed primary | Yes | Local new192 labels_off in-prompt rerun exactly current setting; partial-credit official mean. Supersedes historical labels_on99/n100. Paper EnSI-RAG71.84; sampling/context/backend caveats stay visible. |
| chembench |Open-web150 pilot:113/150=75.33; full closed run71.89/n2785 retained separately | Yes, pilot | scoped primary pilot | Yes only explicitly descriptive subset-vs-full comparison | New branch backup/chembench_openweb_150; DECISIONS885 and samples/chembench_280_seed20260917.json confirm150,native mean0.7533,medium,web_searchlive. HF agent verifying raw. Do not say full benchmark finished under new protocol. |
| medagentsbench |Nine-subset macro50.5074478819 ->50.51, n862 | Yes | primary standalone | No aggregate GSEM bar | Recomputed all862 local detail.json: all n_scored1, no preflight. Dashboard50.65/n860 stale. GSEM publishes five cells, no9-way macro. Include score regardless comparator incomplete; preserve5-subset panel with denominator/judge caveats. |
| biomni_eval1 |Latest ten-task macro59.7565891473 ->59.76, n433 | Yes | historical15-host variant | No primary capability comparison | Sept11 tool_hosts rerun433 valid,0errors. Native61.8937644342 is MICRO and wrong for paper Table1. No data-lake mounted; Sept17 owner requires official E1/lake. Retain59.76 as variant and TODO canonical arm. |
| matscibench |752/1025=73.36585 ->73.37 | Yes | historical15-host variant | No primary capability comparison | Sept18 run_policy audit counted all1025 prompts on retired15-host restricted surface, web_searchdisabled. New open3probe0/3 is not replacement. Retain73.37 with precise surface; TODO new chosen open arm. |
| crag |Truthfulness329/578=0.5692041522 ->0.5692 | Yes | pre-retrieved-KG variant | No primary capability comparison | All578 detail records valid:435 correct,106hallucinations,37missing. Old329/577=.5702 incorrectly dropped idx64 solely because metrics.stage absent; that record is official empty_prediction shortcircuit categorymissing truthfulness0 and must count. Input bypasses mockAPI; native judgeSonnet4.5; paper0.711 differs judge. Retain measurement with caveats and TODO mockAPI rerun. |
| insightbench |Legacy53.6797967033 ->53.68 on91 scored of100 | Yes, conditional legacy score | closed-web/old-judge variant | No primary capability comparison | Closed run detail91. Sept17 openweb100 job mean0 is grading failure:35 recordederrors, judge not available; do not promote0. Required gpt4o rescore pending. Display91coverage and judge. |
| frontierscience_research |Closed-book30/59=50.85 conditional;30/60=50.00 planned set | Yes | closed-book/old-judge variant | No primary capability comparison | No neweropenweb branch. Policy nowopenbook,judgegpt5; originalgpt5.5. Keep50.85n59 (or full-planned50.00 explicitly), TODOopenbook/rejudge. New selectedFrontierAgent63.3. |
| rarebench |161/370=43.51 failed-network run | NO as intended benchmark measurement | diagnostic failed run | No | Every networkattempt failed; current official condition allows web. No fresh network-repaired branch. Keep numerical record only in audit/failure appendix, mark main scoreTODO. |

## Recomputed evidence

Local root `/data1/jiacheng/mentor_results`.

Biomni source: `branches_http/backup__biomni_eval1_tool_hosts/data/biomni_eval1/biomni_eval1__2026-09-11__11-01-07/*/verifier/detail.json`, group `evaluator_record.metrics.task_name`, average reward within each group then equally across10. Success/n: crispr4/10, catalog32/50, opentargets39/50, pharmaprojects37/50, variant13/43, dbqa14/50, seqqa43/50, patient_gene34/50, rare19/30, screen33/50. Config version0.149.1,medium,web_searchdisabled,environmentmountsnull.

MedAgents source: `branches/backup__medagentsbench/data/medagentsbench/medagentsbench__2026-08-31__18-31-56/*/verifier/detail.json`, group `evaluator_record.metrics.dataset`, macro9: MedQA78/100,PubMedQA18/100,MedMCQA50/100,MedBullets62/89,MMLU43/73,MMLU-Pro42/100,MedExQA36/100,MedXpertQA-R51/100,MedXpertQA-U51/100. All862 records n_scored1; no missing grader stage.

CRAG source: `branches/backup__crag/data/crag/crag__2026-09-04__12-15-01/*/verifier/detail.json`; mean `evaluator_record.metrics.truthfulness` all578. idx64 `crag-00064__AW2vs5y` is valid empty answer route, not no measurement.

OOLONG source: `branches_http/backup__oolong_labels_off_192/data/oolong/oolong__2026-09-15__10-29-16`; all192 rewards, mean73.4413167001, empirical SE2.9894627636 percentage points. Use mean/continuous bootstrap interval; not binary Wilson.
