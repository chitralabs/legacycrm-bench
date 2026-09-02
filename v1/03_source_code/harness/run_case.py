#!/usr/bin/env python3
"""Run one benchmark case's acceptance tests against a solution directory.

Usage:
  python run_case.py --case <case_dir> [--solution <dir>|null] [--out results.json]

--solution null runs against an (empty) null solution to measure test discriminative power.
Emits JSON: case id, solution kind, per-test outcomes, pass counts, wall time, exit status.
Deterministic: no network; pytest run with -p no:cacheprovider and PYTHONHASHSEED=0.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent


def run_case(case: Path, solution: str, keep_json: Path | None = None) -> dict:
    case = case.resolve()
    meta = json.loads((case / "case.json").read_text())
    with tempfile.TemporaryDirectory(prefix="lcb_") as tmp:
        report = Path(tmp) / "report.json"
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = "0"
        env["PYTHONPATH"] = str(HARNESS_DIR)
        if solution == "null":
            null_dir = Path(tmp) / "null_solution"
            null_dir.mkdir()
            env["LCB_SOLUTION_DIR"] = str(null_dir)
        elif solution == "reference":
            env["LCB_SOLUTION_DIR"] = str(case / "reference")
        else:
            env["LCB_SOLUTION_DIR"] = str(Path(solution).resolve())
        t0 = time.monotonic()
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", str(case / "tests"), "-q", "--no-header",
                 "-p", "no:cacheprovider", "--json-report", f"--json-report-file={report}"],
                capture_output=True, text=True, env=env, timeout=600,
            )
        except subprocess.TimeoutExpired:
            # a hung candidate (e.g. model-generated infinite loop) is an infra_error
            # result, not a harness crash — required by the protocol's failure handling
            return {
                "case_id": meta["id"], "category": meta["category"],
                "difficulty": meta["difficulty"], "solution": solution,
                "num_tests_expected": meta["num_tests"], "num_tests_collected": 0,
                "num_passed": 0, "pass_rate": 0.0, "all_passed": False,
                "collection_ok": False, "pytest_exit": None, "infra_error": "timeout_600s",
                "wall_seconds": 600.0, "tests": [],
            }
        wall = time.monotonic() - t0
        tests = []
        if report.is_file():
            rep = json.loads(report.read_text())
            for t in rep.get("tests", []):
                tests.append({"nodeid": t["nodeid"], "outcome": t["outcome"]})
        passed = sum(1 for t in tests if t["outcome"] == "passed")
        result = {
            "case_id": meta["id"],
            "category": meta["category"],
            "difficulty": meta["difficulty"],
            "solution": solution,
            "num_tests_expected": meta["num_tests"],
            "num_tests_collected": len(tests),
            "num_passed": passed,
            "pass_rate": (passed / len(tests)) if tests else 0.0,
            "all_passed": bool(tests) and passed == len(tests),
            "collection_ok": len(tests) > 0,
            "pytest_exit": proc.returncode,
            "wall_seconds": round(wall, 3),
            "tests": tests,
        }
        if proc.returncode not in (0, 1):  # 0 all pass, 1 some fail; else infra error
            result["stderr_tail"] = proc.stderr[-2000:]
    if keep_json:
        keep_json.write_text(json.dumps(result, indent=2))
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--solution", default="reference")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    res = run_case(Path(args.case), args.solution, Path(args.out) if args.out else None)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
