#!/usr/bin/env python3
"""Recompute paired comparisons from saved verdicts; makes no model/API calls.

ELAIPBench's four pre-agent failures are replaced by the mentor's completed
September 15 rerun, joined by instance ID. Preserve the original IndustryOR
answer key and the benchmark's official FinanceMath matcher.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np


def elaip_recoveries(manifest_path):
    """Read pinned HF artifacts; only recover the named failed instances."""
    manifest = json.loads(manifest_path.read_text())
    branch = next(b for b in manifest["branches"] if b["branch"] == "backup/elaipbench_rerun4")
    assert len(branch["jobs"]) == 1
    job = branch["jobs"][0]
    stats = job["result"]["stats"]
    assert stats["n_completed_trials"] == 4 and stats["n_errored_trials"] == 0
    assert job["result"]["finished_at"]
    agent = job["config"]["agents"][0]
    assert agent["model_name"] == "azure/gpt-5.6-sol"
    assert agent["kwargs"]["reasoning_effort"] == "medium"
    assert agent["kwargs"]["web_search"] == "disabled"
    evaluations = list(stats["evals"].values())
    assert len(evaluations) == 1
    rewards = evaluations[0]["reward_stats"]["reward"]
    root = manifest_path.parent / branch["branch"].replace("/", "__") / job["path"]
    recovered = {}
    for score, names in rewards.items():
        assert float(score) in (0, 1)
        for name in names:
            path = root / name / "verifier/detail.json"
            detail = json.loads(path.read_text())
            index = detail["instance"]
            assert index == int(name.split("__")[0].rsplit("-", 1)[1])
            assert index not in recovered
            assert detail["reward"] == float(score)
            assert detail["evaluator_record"]["correct"] == bool(float(score))
            recovered[index] = {"detail": detail, "provenance": {
                "instance": index, "trial": name,
                "hf_repository": "gvc-agent-analysis/benchmark-results",
                "hf_branch": branch["branch"], "hf_commit": branch["commit"],
                "job": job["path"], "detail_source": str(path),
                "detail_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "manifest_source": str(manifest_path),
                "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                "job_finished_at": job["result"]["finished_at"],
                "job_n_errors": stats["n_errored_trials"],
                "agent": agent,
            }}
    assert set(recovered) == {42, 43, 251, 252}
    return recovered


def exact_mcnemar(b, c):
    n = b + c
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(b, c) + 1)) / 2 ** n) if n else 1.0


def holm(values):
    order = sorted(range(len(values)), key=values.__getitem__)
    adjusted = [0.0] * len(values)
    previous = 0.0
    for rank, index in enumerate(order):
        previous = max(previous, min(1.0, (len(values) - rank) * values[index]))
        adjusted[index] = previous
    return adjusted


def summarize(pairs, seed):
    counts = {"both_correct": 0, "both_wrong": 0, "codex_only": 0, "comparator_only": 0}
    groups = {}
    for pair in pairs:
        a, b = pair["codex"], pair["comparator"]
        key = "both_correct" if a and b else "codex_only" if a else "comparator_only" if b else "both_wrong"
        counts[key] += 1
        groups.setdefault(pair["resampling_group"], []).append(a - b)
    sums = np.array([sum(group) for group in groups.values()])
    sizes = np.array([len(group) for group in groups.values()])
    rng = np.random.RandomState(seed)
    sampled = rng.randint(0, len(groups), size=(20000, len(groups)))
    boot = sums[sampled].sum(axis=1) / sizes[sampled].sum(axis=1) * 100
    ci = np.percentile(boot, [2.5, 97.5]).tolist()
    signs = rng.randint(0, 2, size=(50000, len(groups))) * 2 - 1
    null = (signs * sums).sum(axis=1)
    permutation_p = (1 + int((np.abs(null) >= abs(sums.sum())).sum())) / 50001
    return {
        "n": len(pairs),
        "codex_correct": sum(pair["codex"] for pair in pairs),
        "comparator_correct": sum(pair["comparator"] for pair in pairs),
        "codex_score": 100 * sum(pair["codex"] for pair in pairs) / len(pairs),
        "comparator_score": 100 * sum(pair["comparator"] for pair in pairs) / len(pairs),
        "delta_pp": 100 * sums.sum() / len(pairs),
        "discordance": counts,
        "mcnemar_exact_p": exact_mcnemar(counts["codex_only"], counts["comparator_only"]),
        "bootstrap_95ci_pp": ci,
        "n_resampling_groups": len(groups),
        "group_signflip_mc_p": permutation_p,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--direct-root", type=Path, default=Path("/data1/jiacheng/mentor_results/branches"))
    parser.add_argument("--comparator-root", type=Path, default=Path("/data1/jiacheng/comparators/_runs"))
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "data/paired_results.json")
    parser.add_argument("--recovery-jobs", type=Path, default=Path(__file__).resolve().parents[1] / "data/hf_refresh/new_jobs.json",
                        help="Saved HF job manifest with ELAIPBench's four completed replacement trials")
    parser.add_argument("--replay", type=Path, help="Recompute from a previously exported paired-results JSON")
    args = parser.parse_args()
    if args.replay:
        result = json.loads(args.replay.read_text())
    else:
        rows = []
        recoveries = elaip_recoveries(args.recovery_jobs)
        specifications = [
            ("financemath", "2026-08-21__22-14-53", "full1"),
            ("elaipbench", "2026-08-23__10-18-54", "medium_full1"),
            ("industryor", "2026-08-22__16-30-58", "full1"),
        ]
        for benchmark, direct_run, comparator_run in specifications:
            source = args.direct_root / ("backup__" + benchmark) / "data" / benchmark / direct_run
            comparator_source = args.comparator_root / benchmark / comparator_run / "score/verdicts.jsonl"
            comp = {}
            for line in comparator_source.read_text().splitlines():
                record = json.loads(line)
                index = record["comparator_run"]["instance"]
                assert index not in comp
                comp[index] = record
            pairs, excluded, recovered_trials, seen = [], [], [], set()
            for path in sorted(source.glob(benchmark + "-*/result.json")):
                trial = json.loads(path.read_text())
                detail = json.loads((path.parent / "verifier/detail.json").read_text())
                index = detail["instance"]
                recovery = recoveries.get(index) if benchmark == "elaipbench" else None
                if trial.get("exception_info"):
                    if recovery is None:
                        excluded.append({"trial": path.parent.name, "reason": trial["exception_info"]["exception_type"]})
                        continue
                    assert trial["exception_info"]["exception_type"] == "NonZeroAgentExitCodeError"
                    for key in ("paper_id", "question_type", "gold"):
                        assert detail["evaluator_record"]["metrics"][key] == recovery["detail"]["evaluator_record"]["metrics"][key]
                    detail = recovery["detail"]
                    recovered_trials.append({**recovery["provenance"],
                        "replaces_trial": path.parent.name,
                        "original_exception": trial["exception_info"]["exception_type"],
                        "recovery_rule": "Replace only a pre-agent failure with its same-instance completed rerun; keep every original observed answer."})
                else:
                    assert recovery is None, "A recovery must never replace an observed original answer"
                assert index not in seen and index in comp
                seen.add(index)
                direct_verdict = detail["evaluator_record"]
                a, b = direct_verdict["correct"], comp[index]["correct"]
                assert isinstance(a, bool) and isinstance(b, bool)
                group = direct_verdict.get("metrics", {}).get("paper_id", index)
                pair = {"instance": index, "codex": int(a), "comparator": int(b), "resampling_group": str(group)}
                if benchmark == "elaipbench":
                    pair["question_type"] = comp[index]["metrics"]["question_type"]
                    assert pair["question_type"] == direct_verdict["metrics"]["question_type"]
                    if recovery is not None:
                        pair["codex_recovery_trial"] = recovery["provenance"]["trial"]
                if benchmark == "industryor":
                    pair["comparator_final_objective"] = comp[index]["comparator_run"]["final_obj"]
                    pair["comparator_repair_changed_answer"] = comp[index]["comparator_run"]["repair_changed_answer"]
                pairs.append(pair)
            if benchmark == "elaipbench":
                assert {item["instance"] for item in recovered_trials} == set(recoveries)
                assert seen == set(comp) and len(pairs) == 403
            rows.append({"benchmark": benchmark, "direct_source": str(source), "comparator_source": str(comparator_source),
                         "excluded_direct_trials": excluded, "recovered_direct_trials": recovered_trials, "pairs": pairs})
        result = {"snapshot": "2026-09-18", "method": {
            "paired_unit": "instance ID; ELAIPBench's four pre-agent failures replaced by completed same-instance September 15 reruns, without replacing any observed original answer",
            "mcnemar": "two-sided exact conditional binomial; Holm across three benchmarks",
            "bootstrap": "20000 paired percentile replicates; paper clusters for ELAIPBench, individual items otherwise",
            "signflip": "50000 two-sided group sign-flip draws plus-one Monte Carlo correction; exploratory symmetry null",
            "seed": 20260918,
        }, "rows": rows}
    for row in result["rows"]:
        row["statistics"] = summarize(row["pairs"], result["method"]["seed"])
        types = sorted({pair["question_type"] for pair in row["pairs"] if "question_type" in pair})
        if types:
            row["question_type_statistics"] = {
                kind: summarize([pair for pair in row["pairs"] if pair["question_type"] == kind], result["method"]["seed"])
                for kind in types
            }
    adjusted = holm([row["statistics"]["mcnemar_exact_p"] for row in result["rows"]])
    for row, value in zip(result["rows"], adjusted):
        row["statistics"]["mcnemar_holm_p"] = value
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for row in result["rows"]:
        print(row["benchmark"], json.dumps(row["statistics"]))


if __name__ == "__main__":
    main()
