#!/usr/bin/env python3
"""Run every benchmark case against a solution kind and write JSONL results.

Usage:
  python run_all.py --solution reference --out ../../05_results/reference_validation.jsonl
  python run_all.py --solution null --out ../../05_results/null_baseline.jsonl

For candidate (model-generated) solutions laid out as <root>/<CASE_ID>/, use:
  python run_all.py --solution-root <root> --out <file>
"""
import argparse
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from run_case import run_case

V1 = Path(__file__).resolve().parent.parent.parent
CASES = V1 / "02_benchmark_dataset" / "cases"


def iter_cases():
    for casejson in sorted(CASES.glob("*/*/case.json")):
        yield casejson.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solution", default=None, help="'reference' or 'null'")
    ap.add_argument("--solution-root", default=None, help="dir with <CASE_ID>/ candidate solutions")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if bool(args.solution) == bool(args.solution_root):
        sys.exit("specify exactly one of --solution / --solution-root")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    results = []
    with open(out, "w") as f:
        header = {
            "run_type": "harness",
            "solution": args.solution or f"root:{args.solution_root}",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "python": sys.version,
            "platform": platform.platform(),
        }
        f.write(json.dumps({"_meta": header}) + "\n")
        for case in iter_cases():
            if args.solution:
                sol = args.solution
            else:
                cid = json.loads((case / "case.json").read_text())["id"]
                sol = str(Path(args.solution_root).resolve() / cid)
            res = run_case(case, sol)
            results.append(res)
            f.write(json.dumps(res) + "\n")
            print(f"{res['case_id']:8s} {res['solution']:>9s} "
                  f"{res['num_passed']}/{res['num_tests_collected']} "
                  f"{'ALL-PASS' if res['all_passed'] else 'FAIL'}")
    n = len(results)
    allp = sum(1 for r in results if r["all_passed"])
    tot_t = sum(r["num_tests_collected"] for r in results)
    tot_p = sum(r["num_passed"] for r in results)
    print(f"\ncases: {n}, all-tests-passed: {allp}, tests passed: {tot_p}/{tot_t}")


if __name__ == "__main__":
    main()
