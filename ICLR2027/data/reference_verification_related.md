# Related-work source verification

Checked 2026-09-19. The old bibliography contained only a dummy example; the related-work
citations were unresolved `TODO:` keys. These were replaced by 19 real references.
Metadata and the associated claims were checked against primary papers, proceedings,
publisher pages, or the authors' official software citation. This is a curated related-work
section, not an exhaustive survey. No numerical results from these papers are imported
into our benchmark comparison.

| BibTeX key | Primary verification source | Claim supported in related work |
| --- | --- | --- |
| `yang2024sweagent` | [NeurIPS 2024 proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html) | Agent interfaces for repository navigation, editing, and execution. |
| `wang2025openhands` | [ICLR 2025 paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/a4b6ad6b48850c0c331d1259fc66a69c-Paper-Conference.pdf) | Generalist agents interact through code, a command line, and a browser. |
| `jimenez2024swebench` | [Authors' benchmark page and BibTeX](https://www.swebench.com/original.html) | Real repository issue-resolution benchmark; ICLR 2024 venue. |
| `mialon2024gaia` | [ICLR 2024 paper](https://proceedings.iclr.cc/paper_files/paper/2024/file/25ae35b5b1738d80f1f03a8713e405ec-Paper-Conference.pdf) | General-assistant tasks involving reasoning, information gathering, and tools. |
| `liu2024agentbench` | [ICLR 2024 proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/hash/e9df36b21ff4ee211a8b71ee8b7e9f57-Abstract-Conference.html) | Evaluation of agents across diverse interactive environments. |
| `chen2025scienceagentbench` | [ICLR 2025 paper](https://openreview.net/pdf?id=6z4YKr0GK6), [author-submitted abstract](https://arxiv.org/abs/2410.05080) | Tasks for rigorous assessment of data-driven scientific discovery. |
| `chan2025mlebench` | [ICLR 2025 paper](https://openreview.net/pdf?id=6s5uXNWGIh), [author-submitted abstract](https://arxiv.org/abs/2410.07095) | Machine-learning engineering tasks and agent evaluation. |
| `wu2024autogen` | [Published COLM 2024 paper](https://openreview.net/pdf/db83d7ffc58f8ea86ddd2bcc9314d43c2bdaa911.pdf), [author institution copy](https://www.microsoft.com/en-us/research/wp-content/uploads/2023/08/LLM_agent.pdf) | Multi-agent conversations and programmable interaction patterns. |
| `khattab2024dspy` | [ICLR 2024 paper](https://proceedings.iclr.cc/paper_files/paper/2024/file/f1cf02ce09757f57c3b93c0db83181e0-Paper-Conference.pdf), [author-submitted abstract](https://arxiv.org/abs/2310.03714) | Optimizing language-model pipelines. |
| `zhang2025aflow` | [ICLR 2025 paper](https://openreview.net/pdf?id=z5uVAKwmjf), [author-submitted abstract](https://arxiv.org/abs/2410.10762) | Search and optimization over agentic workflows. |
| `tang2024medagents` | [ACL Anthology](https://aclanthology.org/2024.findings-acl.33/) | Medical role-based expert discussions; complete published citation and DOI. |
| `bran2024chemcrow` | [Nature Machine Intelligence](https://www.nature.com/articles/s42256-024-00832-8) | Chemistry-specific tools integrated into an LLM agent. |
| `cemri2025mast` | [Author-submitted paper, version 3](https://arxiv.org/abs/2503.13657v3) | Failure taxonomy covering system design, inter-agent misalignment, and task verification. Cited as an arXiv preprint. |
| `zhang2024gsm1k` | [NeurIPS 2024 paper](https://proceedings.neurips.cc/paper_files/paper/2024/file/53384f2090c6a5cac952c598fd67992f-Paper-Datasets_and_Benchmarks_Track.pdf), [author-submitted abstract](https://arxiv.org/abs/2405.00332) | Investigating possible overfitting to an established reasoning benchmark. |
| `sclar2024format` | [ICLR 2024 proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/hash/6c0e99d736da621403018ca7b32b1a4d-Abstract-Conference.html) | Measured performance can change with meaning-preserving prompt formatting. |
| `liang2023helm` | [Published TMLR paper](https://openreview.net/pdf/1882e7aa18c29c4487d64455658f6498456bc0dc.pdf), [author-submitted abstract and full author list](https://arxiv.org/abs/2211.09110) | Standardized multi-scenario, multi-metric model evaluation. |
| `gao2023harness` | [Official repository citation](https://raw.githubusercontent.com/EleutherAI/lm-evaluation-harness/main/CITATION.bib), [software record](https://zenodo.org/records/10256836) | Reusable language-model task and scoring infrastructure; citation refers to v0.4.0. |
| `pineau2021reproducibility` | [JMLR publication](https://jmlr.org/papers/v22/20-303.html) | Code submission, reproducibility checklist, and independent reproduction initiatives. |
| `vandeschoot2021asreview` | [Nature Machine Intelligence](https://www.nature.com/articles/s42256-020-00287-7), [authors' project page](https://asreview.nl/project/intro_paper_asreview/) | Transparent active-learning-assisted literature screening, not autonomous validation of claims. |

## Metadata choices and scope

- Published year is used when a proceedings or journal version is verified; it can differ
  from the first arXiv upload year. MAST is recorded as a preprint without an inferred venue.
- GAIA's published PDF includes Craig Swift, who is omitted from the proceedings landing
  page. The bibliography follows the PDF.
- OpenHands' published PDF gives Yanjun Shao and Hoang H. Tran; the landing page uses
  different display-name variants. The bibliography follows the PDF.
- ScienceAgentBench's ICLR PDF gives Zevi Liao; the arXiv metadata spells the name Zeyi
  Liao. The bibliography follows the cited conference PDF.
- DSPy's proceedings landing page retains the older title ending in “State-of-the-Art
  Pipelines”; the published PDF and current author-submitted abstract use “Self-Improving
  Pipelines”, which is used here.
- AutoGen's COLM PDF uses the plural “Conversations” and includes Jiale Liu; the
  bibliography follows the PDF rather than the institution's abbreviated metadata.
- Sources support the description of prior work. Our workflow-length, decomposition,
  and domain-convention mechanisms are study questions and trace interpretations;
  citations do not substitute for our own causal ablations.
- Some OpenReview PDF endpoints returned a browser-verification page on direct open;
  their primary-source search-index text and author-submitted or proceedings copies were
  used to cross-check the bibliographic metadata. No secondary summary was treated as
  authoritative evidence.
