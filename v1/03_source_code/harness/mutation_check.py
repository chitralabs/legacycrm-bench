#!/usr/bin/env python3
"""Mutation-sensitivity analysis of LegacyCRM-Bench acceptance tests.

For every case with Python deliverables, applies simple first-order mutations to the
*reference* solution (one mutation per run) and re-runs the acceptance tests. A mutant is
"killed" if at least one test fails. High kill rates are evidence that the test oracles are
sensitive to behavioral deviations; surviving mutants are listed for manual triage
(equivalent mutant vs. test gap).

Mutation operators (deterministic, AST-based):
  ROR: > <-> >=, < <-> <=, == <-> !=
  AOR: + <-> -, * <-> / (BinOp only)
  CBR: True <-> False constants
  SVR: short string constants (1-12 chars) anywhere in the module: append "_X"; note this
       includes constants outside comparisons, so some SVR mutants are expected to be
       equivalent (triage classifies survivors)
Usage: python mutation_check.py [--case <dir>] --out <results.jsonl>
"""
import argparse
import ast
import copy
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from run_case import run_case

V1 = Path(__file__).resolve().parent.parent.parent
CASES = V1 / "02_benchmark_dataset" / "cases"

ROR = {ast.Gt: ast.GtE, ast.GtE: ast.Gt, ast.Lt: ast.LtE, ast.LtE: ast.Lt,
       ast.Eq: ast.NotEq, ast.NotEq: ast.Eq}
AOR = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Div, ast.Div: ast.Mult}


def find_mutations(tree):
    """Yield (path_id, description, mutate_fn) where mutate_fn(tree_copy) applies the mutation."""
    muts = []
    for i, node in enumerate(ast.walk(tree)):
        if isinstance(node, ast.Compare) and len(node.ops) == 1 and type(node.ops[0]) in ROR:
            muts.append((i, f"ROR:{type(node.ops[0]).__name__}", "ror"))
        elif isinstance(node, ast.BinOp) and type(node.op) in AOR:
            muts.append((i, f"AOR:{type(node.op).__name__}", "aor"))
        elif isinstance(node, ast.Constant) and node.value is True or (
                isinstance(node, ast.Constant) and node.value is False):
            muts.append((i, "CBR:bool", "cbr"))
        elif (isinstance(node, ast.Constant) and isinstance(node.value, str)
              and 1 <= len(node.value) <= 12 and node.value.strip()):
            muts.append((i, f"SVR:{node.value[:8]!r}", "svr"))
    return muts


def apply_mutation(tree, index, kind):
    tree = copy.deepcopy(tree)
    for i, node in enumerate(ast.walk(tree)):
        if i != index:
            continue
        if kind == "ror" and isinstance(node, ast.Compare):
            node.ops[0] = ROR[type(node.ops[0])]()
        elif kind == "aor" and isinstance(node, ast.BinOp):
            node.op = AOR[type(node.op)]()
        elif kind == "cbr" and isinstance(node, ast.Constant):
            node.value = not node.value
        elif kind == "svr" and isinstance(node, ast.Constant):
            node.value = node.value + "_X"
        else:
            return None
        return tree
    return None


def mutants_for_case(case: Path, cap: int):
    """Deterministically pick up to `cap` mutants per case, spread across operators/files."""
    out = []
    for py in sorted((case / "reference").glob("*.py")):
        tree = ast.parse(py.read_text())
        for index, desc, kind in find_mutations(tree):
            out.append((py.name, index, desc, kind))
    # even spread: take every k-th to cap
    if len(out) > cap:
        step = len(out) / cap
        out = [out[int(i * step)] for i in range(cap)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default=None)
    ap.add_argument("--cap", type=int, default=12, help="max mutants per case")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    cases = ([Path(args.case)] if args.case
             else sorted(p.parent for p in CASES.glob("*/*/case.json")))
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    total = killed = 0
    with open(outp, "w") as f:
        f.write(json.dumps({"_meta": {
            "run_type": "mutation_check", "cap_per_case": args.cap,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "python": sys.version}}) + "\n")
        for case in cases:
            meta = json.loads((case / "case.json").read_text())
            deliverables = meta["deliverables"]
            muts = mutants_for_case(case, args.cap)
            for fname, index, desc, kind in muts:
                src_tree = ast.parse((case / "reference" / fname).read_text())
                mtree = apply_mutation(src_tree, index, kind)
                if mtree is None:
                    continue
                with tempfile.TemporaryDirectory(prefix="lcb_mut_") as tmp:
                    sol = Path(tmp) / "solution"
                    sol.mkdir()
                    for d in deliverables:
                        shutil.copy(case / "reference" / d, sol / d)
                    try:
                        (sol / fname).write_text(ast.unparse(mtree))
                    except Exception as e:
                        continue
                    res = run_case(case, str(sol))
                is_killed = not res["all_passed"]
                total += 1
                killed += is_killed
                f.write(json.dumps({
                    "case_id": meta["id"], "file": fname, "node_index": index,
                    "operator": desc, "killed": is_killed,
                    "passed": res["num_passed"], "collected": res["num_tests_collected"],
                    "pytest_exit": res["pytest_exit"],  # distinguishes assertion kills (1) from infra errors
                }) + "\n")
            print(f"{meta['id']}: {len(muts)} mutants")
    print(f"\nmutants: {total}, killed: {killed}, kill rate: "
          f"{(killed / total * 100 if total else 0):.1f}%")


if __name__ == "__main__":
    main()
