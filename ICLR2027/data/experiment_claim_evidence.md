# Experiment claims and saved evidence

Verified on 2026-09-19 for the revision of `4_experiments.tex`. No new model calls or experiment jobs were launched. This ledger supports selected trace examples; it does not provide a mechanism-prevalence estimate or causal component ablation.

## Pair population and numbering

`paired_results.json` preserves the pre-existing 703 pairs. Discordant outcomes: ELAIPBench 101 (34 Codex-only / 67 specialized-only), FinanceMath 20 (10 / 10), IndustryOR 9 (6 / 3), total 130. Benchmark-level published reference comparisons remain 7 higher, 4 lower, 9 unclassified across the main 20; the abstract's draft 45% on-par statement is not used as measured equivalence.

FinanceMath case IDs below are `validation-N`, corresponding to zero-based `financemath-N` instances. Comparator JSONL file order differs from instance order: join on `id`, never line number. IndustryOR uses one-based `paper_problem_id = instance + 1`; chat-log records are zero-based by `index`.

## Finding 1: More stages do not ensure higher accuracy

- Completed paired totals remain FinanceMath 158/200 for both arms; IndustryOR 73/100 Codex, 70/100 ReLoop; ELAIPBench 151/403 Codex, 184/403 AgentSPEX-medium. These outcomes neither establish equivalence nor show complexity as the causal source of a gap.
- ReLoop's saved stage columns yield 69/100 after initial generation (`cot`), 70/100 after L1 execution verification and regeneration (`l1`), 70/100 after L2 behavioral checks (`l2`), and 70/100 after final repair. Only problem16 (instance15) is newly correct after repair. Its extractor specifies `timing=beginning_of_each_month`; initial generated code insists on exact `beginning` and raises ValueError. Repair removes that brittle check and applies purchases-before-sales constraints, obtaining 4100. These are sequential stage readouts, not independent randomized ablations. Codex also solves this case.
- IndustryOR problems52,80,82,96 all receive three repair prompts and finish with null objective; Codex solves them. ID52 also encounters a missing SciPy dependency. These failures cannot all be assigned to reasoning.

## Finding 2: Information can fail to survive a handoff

- ReLoop problem82 (instance81): extractor stores `minimum_number_of_shops`; generator prompt exposes only `store_types: list[5] of dict`; generated code checks aliases `min`, `minimum`, `min_shops`, `minimum_shops` and raises KeyError. Original natural-language problem remains available, but generated-code schema is omitted.
- Related failures: problem52 extractor field `required_number_of_drivers_and_crew_members` is hidden behind `time_periods: list[6] of dict`, code guesses `required_number`; problem96 cutting-demand and extra-cost fields are hidden in nested list/dict representations.
- FinanceMath validation147: catalog claims C4 and C7 identify the three-year return 6.2% and ratio 0.6078. The market marks C4 uncertain, and final code averages returns from four horizons (5.3,6.2,4.7,4.4) before dividing by10.2, yielding0.5049. Codex's original task includes labeled table horizons; its executed program uses6.2/10.2, submitted0.607843137254902, and earns reward1. This demonstrates downstream failure to use an extracted relevant relation, not literal removal of every occurrence of the fact. Full-schema/context-retention interventions remain pending.

## Finding 3: Useful domain constraints and checks

- FinanceMath validation92: MoCA catalog C3 records original1year minus elapsed3months =0.75years; C5 selects the remaining three discount factors. Program returns100.753663; Codex uses four factors and returns100.5241705. Native evaluator credits MoCA and rejects Codex. The example supports preservation of a time condition; component-specific benefit is untested.
- FinanceMath validation121: MoCA explicitly computes HKD/CNY × CNY/AUD, yielding5.96844105; Codex computes the reciprocal0.16754793950758717. Native evaluator credits MoCA and rejects Codex. The catalog prose includes an arithmetic typo5.96744105, so use executed `agent_answer`/`code_output`, not that prose, for the number. Wording admits quote-direction ambiguity; interpret as alignment to the reference convention, not an unconditional mathematical defect.
- IndustryOR problem6 (instance5): Codex executes an integer model obtaining10755, then deliberately converts production/inventory/backlog to continuous and submits10750. ReLoop retains integer variables and submits10755, the reference. This is a convention/model-domain divergence after a successful integer computation, not inability to calculate10755. A counterfactual domain-verification intervention has not been run.
- ELAIPBench's67 specialized-only successes and gains in both question types motivate a broader paper-evidence/qualification/verification audit. Existing outcome counts do not identify the responsible component.
- Tool pilots record availability/use only, not causal accuracy effects; preserved MatSci10zero-search and Biomni4domain-service observations from `trace_evidence.json`.

## Answer delivery and negative controls

- IndustryOR problem28 (instance27): saved Codex trace executes objective580000 twice, but submitted objective prose begins `Maximize V=1.2x_3+...`; the official grader extracts1.2 and scores0. This is a selected case of correct computation but failed delivery, not evidence that such failures dominate Codex errors. Main score remains unchanged.
- Do not use IndustryOR problem47 (instance46) to attribute specialized superiority to a mechanism: verifier records historical gold20241.6153846 versus current gold20241.8, and Codex20241.8 has `correct_current=true`. Its paired main verdict remains based on the original key, but the disagreement is confounded by answer-key drift.
- Domain-specific conventions/task-condition preservation have concrete case evidence; targeted semantic-verification gains, systematic context-retention advantage, and delivery-failure prevalence remain pending. The paper preserves explicit TODOs for these tests.

## Source checksums

| Source | SHA-256 |
|---|---|
| `/home/jiacheng/iclr2027_paper/data/paired_results.json` | `16b4d372fa4d25d79ebfe328a56b328863ab61cb776c466802cea630470a4a4d` |
| `/home/jiacheng/iclr2027_paper/data/trace_evidence.json` | `40b72022a0bde82b974e9dc77156e78a5584d3ed645a4b701a40b1f0c2bf3ca2` |
| `/data1/jiacheng/comparators/_runs/financemath/full1/financemath.jsonl` | `b4bd13d520c39f4a4a13fe8cc195bd3584d1bb64712044723f056d34b8165843` |
| `/data1/jiacheng/comparators/_runs/industryor/full1/out/chat_logs.jsonl` | `967ac066a068ab4ae41460eec26bc9983ccfb07268c99fa785b4b1e6540d3bc6` |
| `/data1/jiacheng/comparators/_runs/industryor/full1/out/ablation_report.csv` | `54b50fe5a4afcfdaba8d804c316eb564812032743a2a736418797f3aab9cfa01` |
| `/data1/jiacheng/mentor_results/branches/backup__financemath/data/financemath/2026-08-21__22-14-53/financemath-00092__3SiLQ4A/verifier/detail.json` | `027175ec2a68be451d54a8c9a70bcaf47aa3975bec7489daabebc3dd152c85e0` |
| `/data1/jiacheng/mentor_results/branches/backup__financemath/data/financemath/2026-08-21__22-14-53/financemath-00092__3SiLQ4A/agent/trajectory.json` | `759bbf691da2ded27913a40e64a37201a18def81648ac9c459183246321cffa4` |
| `/data1/jiacheng/mentor_results/branches/backup__financemath/data/financemath/2026-08-21__22-14-53/financemath-00121__QByuuzJ/verifier/detail.json` | `6053b0029783a70290b7ec7f690b967d81730686aa03c5496ec1e2ee351836c0` |
| `/data1/jiacheng/mentor_results/branches/backup__financemath/data/financemath/2026-08-21__22-14-53/financemath-00121__QByuuzJ/agent/trajectory.json` | `8a4be3f56d7e9ff26afaa558d135f7b5de23dfb2e51b884fc6c0563d3823e01e` |
| `/data1/jiacheng/mentor_results/branches/backup__financemath/data/financemath/2026-08-21__22-14-53/financemath-00147__mPuFuPh/verifier/detail.json` | `ed98be00afddad1002b650a0dfc7aa2406e7600d137b6e2faeaf24c6e01c881a` |
| `/data1/jiacheng/mentor_results/branches/backup__financemath/data/financemath/2026-08-21__22-14-53/financemath-00147__mPuFuPh/agent/trajectory.json` | `e14b2785ba4c177ca3296c746d7d281c6913d21a80ca360a0e5c2fe561a2d455` |
| `/data1/jiacheng/mentor_results/branches/backup__industryor/data/industryor/2026-08-22__16-30-58/industryor-00005__8jxQSAZ/verifier/detail.json` | `515ba802c4952f003be0cd2ea5b9c3f29a2659f589154fb1d3ea49f54a94de71` |
| `/data1/jiacheng/mentor_results/branches/backup__industryor/data/industryor/2026-08-22__16-30-58/industryor-00005__8jxQSAZ/agent/trajectory.json` | `70b20e2263155b91dee7a2333cdf056bb26c4fd9fe4b58d8e97aececdb9364ee` |
| `/data1/jiacheng/mentor_results/branches/backup__industryor/data/industryor/2026-08-22__16-30-58/industryor-00015__J7tctm2/verifier/detail.json` | `f8e9080662be3c8653563d3bd4201b9e068ebc5560f059023071e210de94cd1e` |
| `/data1/jiacheng/mentor_results/branches/backup__industryor/data/industryor/2026-08-22__16-30-58/industryor-00015__J7tctm2/agent/trajectory.json` | `2055f9946b6987457f32f7452adf6b363570744c6708d676055927bb10cd1846` |
| `/data1/jiacheng/mentor_results/branches/backup__industryor/data/industryor/2026-08-22__16-30-58/industryor-00027__Wj9bSTh/verifier/detail.json` | `ff6eda82d5c0f5d878dada5bd3e96f1bb22810e1a9de5f6051c56067cf1df47e` |
| `/data1/jiacheng/mentor_results/branches/backup__industryor/data/industryor/2026-08-22__16-30-58/industryor-00027__Wj9bSTh/agent/trajectory.json` | `a10b9cd896a534581eeaa480b43d20cf1c319c870a2e893c36aebf1f3f80e1d1` |
| `/data1/jiacheng/mentor_results/branches/backup__industryor/data/industryor/2026-08-22__16-30-58/industryor-00046__eGa6guB/verifier/detail.json` | `0bf2a7bf7307b33aef8f9e2275d1c80d2ff223e1f50dbce8313d1bbbece1097e` |
| `/data1/jiacheng/mentor_results/branches/backup__industryor/data/industryor/2026-08-22__16-30-58/industryor-00046__eGa6guB/agent/trajectory.json` | `0aca4bd47875ff1a9ee64eb5ff602f1df83ef0239489e55c18fbc8db95034d56` |
