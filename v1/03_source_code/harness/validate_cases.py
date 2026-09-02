#!/usr/bin/env python3
"""Structural validator for LegacyCRM-Bench cases (contract: 02_benchmark_dataset/CASE_FORMAT.md).

Checks per case: required files, case.json schema, id/category/difficulty validity, deliverables
present in reference/, no extra files in reference/, tests reference case_lib solution loading,
no network imports in tests or reference, num_tests consistency is checked by run_all (collected).
Exit code 0 iff no errors.
"""
import json
import re
import sys
from pathlib import Path

V1 = Path(__file__).resolve().parent.parent.parent
CASES = V1 / "02_benchmark_dataset" / "cases"

CATS = {
    "schema_mapping": "SCH", "validation_rules": "VAL", "workflows": "WFL",
    "legacy_scripts": "SCR", "rbac": "RBC", "integration": "INT",
    "batch_processing": "BAT", "error_handling": "ERR", "audit_logging": "AUD",
    "referential_integrity": "RIN", "business_rules": "BIZ", "config_modernization": "CFG",
}
REQ_FIELDS = ["id", "title", "category", "difficulty", "source_artifacts", "target_requirement",
              "expected_behavior", "deliverables", "dependencies", "provenance", "license",
              "ground_truth_derivation", "security_expectations", "failure_conditions", "num_tests"]
FORBIDDEN = re.compile(r"^\s*(import|from)\s+(requests|urllib|http\.client|socket|subprocess)\b", re.M)


def check_case(case: Path, errors: list):
    rel = case.relative_to(CASES)
    def err(msg):
        errors.append(f"{rel}: {msg}")

    for f in ["case.json", "target_spec.md", "GROUND_TRUTH.md"]:
        if not (case / f).is_file():
            err(f"missing {f}")
    for d in ["legacy", "tests", "reference"]:
        if not (case / d).is_dir():
            err(f"missing {d}/")
    cj = case / "case.json"
    if not cj.is_file():
        return
    try:
        meta = json.loads(cj.read_text())
    except json.JSONDecodeError as e:
        err(f"case.json invalid JSON: {e}")
        return
    for f in REQ_FIELDS:
        if f not in meta:
            err(f"case.json missing field {f}")
    cat = meta.get("category")
    if cat != case.parent.name:
        err(f"category {cat!r} != directory {case.parent.name!r}")
    prefix = CATS.get(case.parent.name)
    if prefix and not re.fullmatch(rf"{prefix}-\d{{2}}", meta.get("id", "")):
        err(f"id {meta.get('id')!r} does not match {prefix}-NN")
    if meta.get("id") != case.name:
        err(f"id {meta.get('id')!r} != case dir name {case.name!r}")
    if meta.get("difficulty") not in ("easy", "medium", "hard"):
        err(f"bad difficulty {meta.get('difficulty')!r}")
    if not isinstance(meta.get("num_tests"), int) or meta.get("num_tests", 0) < 8:
        err(f"num_tests must be int >= 8 (got {meta.get('num_tests')!r})")
    for d in meta.get("deliverables", []):
        if not (case / "reference" / d).is_file():
            err(f"deliverable {d} missing from reference/")
    if (case / "reference").is_dir():
        extra = [p.name for p in (case / "reference").iterdir()
                 if p.name not in set(meta.get("deliverables", [])) and p.name != "__pycache__"]
        if extra:
            err(f"extra files in reference/: {extra}")
    tests = list((case / "tests").glob("test_*.py")) if (case / "tests").is_dir() else []
    if not tests:
        err("no test_*.py in tests/")
    n_test_funcs = 0
    for t in tests:
        src = t.read_text()
        if "case_lib" not in src:
            err(f"{t.name} does not use case_lib solution loading")
        if FORBIDDEN.search(src):
            err(f"{t.name} imports forbidden module (network/subprocess)")
        try:
            import ast as _ast
            tree = _ast.parse(src)
            n_test_funcs += sum(1 for n in _ast.walk(tree)
                                if isinstance(n, _ast.FunctionDef) and n.name.startswith("test_"))
        except SyntaxError as e:
            err(f"{t.name} has a syntax error: {e}")
    if isinstance(meta.get("num_tests"), int):
        if n_test_funcs != meta["num_tests"]:
            err(f"num_tests={meta['num_tests']} but {n_test_funcs} test functions found")
        if meta["num_tests"] > 25:
            err(f"num_tests={meta['num_tests']} exceeds the contract hard cap of 25")
    for r in (case / "reference").glob("*.py") if (case / "reference").is_dir() else []:
        if FORBIDDEN.search(r.read_text()):
            err(f"reference/{r.name} imports forbidden module")
    for a in meta.get("source_artifacts", []):
        if not (case / a).is_file():
            err(f"source_artifact {a} not found in case dir")


def main():
    errors = []
    cases = sorted(CASES.glob("*/*/case.json"))
    if not cases:
        print("no cases found")
        sys.exit(1)
    for cj in cases:
        check_case(cj.parent, errors)
    ids = [json.loads(c.read_text()).get("id") for c in cases]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        errors.append(f"duplicate case ids: {sorted(dupes)}")
    print(f"validated {len(cases)} cases; {len(errors)} errors")
    for e in errors:
        print(" ERROR:", e)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
