#!/usr/bin/env python3
"""Aggregate harness result JSONL files into the tables used by the manuscript.

Inputs (05_results/): reference_validation.jsonl, null_baseline.jsonl, mutation_results.jsonl
Outputs (06_figures_tables/):
  T1_benchmark_composition.csv  — cases/tests per category & difficulty (from case.json files)
  T2_groundtruth_validation.csv — per-category reference vs null pass rates
  T3_mutation_sensitivity.csv   — per-category mutant counts and kill rates
  surviving_mutants.csv         — every surviving mutant for manual triage
Every number in these tables is computed here from raw JSONL/case.json — no hand entry.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

V1 = Path(__file__).resolve().parent.parent.parent
RES = V1 / "05_results"
OUT = V1 / "06_figures_tables"
CASES = V1 / "02_benchmark_dataset" / "cases"


def read_jsonl(name):
    rows = []
    with open(RES / name) as f:
        for line in f:
            d = json.loads(line)
            if "_meta" not in d:
                rows.append(d)
    return rows


def main():
    OUT.mkdir(exist_ok=True)
    metas = [json.loads(p.read_text()) for p in sorted(CASES.glob("*/*/case.json"))]

    # T1 composition
    comp = defaultdict(lambda: {"cases": 0, "tests": 0, "easy": 0, "medium": 0, "hard": 0})
    for m in metas:
        c = comp[m["category"]]
        c["cases"] += 1
        c["tests"] += m["num_tests"]
        c[m["difficulty"]] += 1
    with open(OUT / "T1_benchmark_composition.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["category", "cases", "easy", "medium", "hard", "acceptance_tests"])
        for cat in sorted(comp):
            c = comp[cat]
            w.writerow([cat, c["cases"], c["easy"], c["medium"], c["hard"], c["tests"]])
        t = {k: sum(c[k] for c in comp.values()) for k in ["cases", "easy", "medium", "hard", "tests"]}
        w.writerow(["TOTAL", t["cases"], t["easy"], t["medium"], t["hard"], t["tests"]])

    # T2 reference vs null
    ref = {r["case_id"]: r for r in read_jsonl("reference_validation.jsonl")}
    nul = {r["case_id"]: r for r in read_jsonl("null_baseline.jsonl")}
    bycat = defaultdict(lambda: {"cases": 0, "ref_t": 0, "ref_p": 0, "nul_t": 0, "nul_p": 0, "ref_allpass": 0})
    for m in metas:
        r, n = ref.get(m["id"]), nul.get(m["id"])
        c = bycat[m["category"]]
        c["cases"] += 1
        if r:
            c["ref_t"] += r["num_tests_collected"]; c["ref_p"] += r["num_passed"]
            c["ref_allpass"] += int(r["all_passed"])
        if n:
            c["nul_t"] += n["num_tests_collected"]; c["nul_p"] += n["num_passed"]
    with open(OUT / "T2_groundtruth_validation.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["category", "cases", "reference_tests_passed", "reference_tests_total",
                    "reference_cases_all_pass", "null_tests_passed", "null_tests_total"])
        for cat in sorted(bycat):
            c = bycat[cat]
            w.writerow([cat, c["cases"], c["ref_p"], c["ref_t"], c["ref_allpass"], c["nul_p"], c["nul_t"]])
        w.writerow(["TOTAL", sum(c["cases"] for c in bycat.values()),
                    sum(c["ref_p"] for c in bycat.values()), sum(c["ref_t"] for c in bycat.values()),
                    sum(c["ref_allpass"] for c in bycat.values()),
                    sum(c["nul_p"] for c in bycat.values()), sum(c["nul_t"] for c in bycat.values())])

    # T3 mutation
    mut_path = RES / "mutation_results.jsonl"
    if mut_path.is_file():
        muts = read_jsonl("mutation_results.jsonl")
        cat_of = {m["id"]: m["category"] for m in metas}
        mc = defaultdict(lambda: {"mutants": 0, "killed": 0})
        surv = []
        for r in muts:
            c = mc[cat_of.get(r["case_id"], "?")]
            c["mutants"] += 1
            c["killed"] += int(r["killed"])
            if not r["killed"]:
                surv.append(r)
        with open(OUT / "T3_mutation_sensitivity.csv", "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["category", "mutants", "killed", "kill_rate_pct"])
            for cat in sorted(mc):
                c = mc[cat]
                w.writerow([cat, c["mutants"], c["killed"], round(c["killed"] / c["mutants"] * 100, 1)])
            tm = sum(c["mutants"] for c in mc.values()); tk = sum(c["killed"] for c in mc.values())
            w.writerow(["TOTAL", tm, tk, round(tk / tm * 100, 1) if tm else 0])
        with open(OUT / "surviving_mutants.csv", "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["case_id", "file", "node_index", "operator", "passed", "collected"])
            for r in surv:
                w.writerow([r["case_id"], r["file"], r["node_index"], r["operator"],
                            r["passed"], r["collected"]])
    print("tables written to", OUT)


if __name__ == "__main__":
    main()
