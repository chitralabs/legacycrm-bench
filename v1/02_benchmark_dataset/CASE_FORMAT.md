# LegacyCRM-Bench Case Format (v0.1)

Every benchmark case lives in `02_benchmark_dataset/cases/<category>/<CASE_ID>/` and contains
exactly these elements. The structural validator (`03_source_code/harness/validate_cases.py`)
enforces this contract.

## Directory layout

```
cases/<category>/<CASE_ID>/
  case.json               # machine-readable metadata (schema below)
  legacy/                 # the legacy source artifacts for this task (copied/excerpted from legacy_system/)
  target_spec.md          # target requirement: exact deliverable files + interfaces + behavior
  tests/test_acceptance.py# executable pytest acceptance tests
  reference/              # ground-truth reference solution (must pass all tests)
  GROUND_TRUTH.md         # how expected behavior was derived from documented legacy semantics
```

## Case identifiers

`<CAT>-<NN>` where CAT ∈ {SCH, VAL, WFL, SCR, RBC, INT, BAT, ERR, AUD, RIN, BIZ, CFG} and NN is
two digits, e.g. `RBC-02`. Category directories:

| Dir | CAT | Coverage requirement satisfied |
|---|---|---|
| schema_mapping | SCH | Schema and field mapping |
| validation_rules | VAL | Validation rules |
| workflows | WFL | Business workflows |
| legacy_scripts | SCR | Legacy scripts |
| rbac | RBC | Role-based access controls |
| integration | INT | Integration interfaces |
| batch_processing | BAT | Batch processing |
| error_handling | ERR | Error handling |
| audit_logging | AUD | Audit logging |
| referential_integrity | RIN | Referential integrity |
| business_rules | BIZ | Business-rule preservation |
| config_modernization | CFG | Configuration modernization |

## case.json schema (all fields required)

```json
{
  "id": "RBC-02",
  "title": "Short human title",
  "category": "rbac",
  "difficulty": "easy | medium | hard",
  "source_artifacts": ["legacy/role_permissions.csv", "..."],
  "target_requirement": "One-paragraph summary of what must be produced (full detail in target_spec.md).",
  "expected_behavior": "One-paragraph summary of observable behavior the tests check.",
  "deliverables": ["migrated.py"],
  "dependencies": {"python": ">=3.10", "packages": []},
  "provenance": "Synthetic; authored for LegacyCRM-Bench from Meridian CRM 4.2 spec (SYSTEM_OVERVIEW.md).",
  "license": "Code: MIT; data/specs: CC BY 4.0",
  "ground_truth_derivation": "Pointer to GROUND_TRUTH.md",
  "security_expectations": "What must NOT happen (e.g., no credential literals, no privilege widening).",
  "failure_conditions": "What counts as failure beyond test failures (e.g., network access, nondeterminism).",
  "num_tests": 12
}
```

## Test contract

- Tests are plain pytest, Python stdlib only (plus `pytest` itself). No network, no wall-clock
  dependence (any 'today' is injected), no randomness without a fixed seed.
- Tests locate the candidate solution via the environment variable `LCB_SOLUTION_DIR`
  (absolute path). If unset, tests default to the case's own `reference/` directory. Standard
  loader helpers live in `03_source_code/harness/case_lib.py` (importable as `case_lib` because
  the harness prepends it to `sys.path`); use `case_lib.solution_dir()` and
  `case_lib.load_solution_module("migrated")`.
- Deliverables are files the migration must produce (Python modules, JSON/SQL/config files) as
  named in `deliverables`. Tests must fail cleanly (not error the collection) when deliverables
  are missing — import inside fixtures/tests, not at module top level.
- Each test function asserts one observable behavior; aim for 8–20 tests/case (hard cap 25). At least one test
  must encode a *negative* expectation (behavior that must be rejected/absent), and for cases
  with `security_expectations`, at least one test enforces them (e.g., scanning delivered files
  for credential literals, asserting deny-by-default).
- Every expected value must be derivable by hand from `legacy_system/SYSTEM_OVERVIEW.md` +
  the case's legacy artifacts; the derivation is written in `GROUND_TRUTH.md`. LLM-derived
  expectations are forbidden.

## Reference solution contract

- `reference/` contains exactly the files named in `deliverables`, plus nothing else.
- Must pass 100% of the case's tests under `LCB_SOLUTION_DIR=<case>/reference`.
- Stdlib only; deterministic; no network. `sqlite3` is allowed (stdlib).
- Written by a human-directed process against the documented semantics; it is a *reference*,
  not necessarily the only correct solution — tests, not the reference, define correctness.

## Difficulty rubric

- **easy**: single artifact, ≤ 2 interacting legacy conventions (e.g., sentinel dates), direct mapping.
- **medium**: 2–3 artifacts or conventions interact (e.g., rules + soft delete + currency default).
- **hard**: cross-entity logic, ordering/rounding/hysteresis subtleties, or security-critical
  semantics where a plausible-but-wrong migration passes naive checks.
