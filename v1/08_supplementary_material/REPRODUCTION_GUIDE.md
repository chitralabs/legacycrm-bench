# Reproduction Guide — LegacyCRM-Bench v0.1

Environment used for all executed results in `05_results/` (recorded 2026-09-01):
macOS (Darwin 24.6.0, Apple Silicon), Python 3.14.2 (Homebrew), dependencies pinned in
`03_source_code/requirements.txt`. Everything is offline and deterministic
(PYTHONHASHSEED=0 enforced by the harness; fixed seed 20260901 for data generation).

## Steps

```bash
cd v1
python3 -m venv .venv
.venv/bin/pip install -r 03_source_code/requirements.txt

# 1. Regenerate seed data; verify byte-identical output
.venv/bin/python 03_source_code/generate_seed_data.py
shasum 02_benchmark_dataset/legacy_system/seed_data/*.csv

# 2. Structural validation of all 36 cases (expect: 0 errors)
.venv/bin/python 03_source_code/harness/validate_cases.py

# 3. Ground-truth validation — write to a NEW file so the archived results are never
#    overwritten, then diff against the archived run (expect: every case all-tests-pass)
.venv/bin/python 03_source_code/harness/run_all.py --solution reference \
    --out 05_results/repro_reference_validation.jsonl

# 4. Null-baseline control (expect: 0 tests pass anywhere)
.venv/bin/python 03_source_code/harness/run_all.py --solution null \
    --out 05_results/repro_null_baseline.jsonl

# 5. Mutation-sensitivity analysis (deterministic; slowest step, ~10-15 min)
.venv/bin/python 03_source_code/harness/mutation_check.py \
    --out 05_results/repro_mutation_results.jsonl

# 6. Compare against the archived results (only the _meta timestamp lines may differ)
for f in reference_validation null_baseline mutation_results; do
  diff <(grep -v '_meta' "05_results/$f.jsonl") \
       <(grep -v '_meta' "05_results/repro_$f.jsonl") \
    && echo "$f: identical" || echo "$f: DIFFERS - investigate"
done

# 7. Verify archived-file integrity
shasum -a 256 -c 05_results/SHA256SUMS

# 8. Regenerate manuscript tables + input-size measurements (reads archived results)
.venv/bin/python 03_source_code/analysis/aggregate.py
.venv/bin/python 03_source_code/analysis/measure_inputs.py
```

Timestamps inside JSONL `_meta` headers will differ across reproductions; all other content is
deterministic.

## Model-run analysis (executed 2026-09-01/02)

The paid model runs (P1–P3) are inherently non-rerunnable bit-for-bit (provider
nondeterminism), so reproduction means re-deriving every table from the archived raw logs:

```bash
shasum -a 256 -c 05_results/model_runs/SHA256SUMS   # verify raw-log integrity
.venv/bin/python 03_source_code/analysis/model_analysis.py   # M1-M5 + run_disposition
.venv/bin/python 03_source_code/analysis/make_tex_tables.py  # LaTeX tables + macros
```

The C5 transpiler baseline IS rerunnable end-to-end at zero cost:
`.venv/bin/python 03_source_code/runner/transpiler_c5.py --out-root /tmp/c5_repro`.
Sandbox verification: `.venv/bin/python 03_source_code/runner/probe.py` (7/7 checks).

The independent second-platform reproduction has been COMPLETED: the repository's Linux
continuous-integration workflow (ubuntu, Python 3.13) reproduces seed bytes, case
validation, per-test reference/null outcomes, per-mutant kill outcomes, and byte-identical
regeneration of all tables/macros/bibliography on every push; the archived first run is
documented in `SECOND_PLATFORM_REPRODUCTION.md`. Model runs remain non-rerunnable
bit-for-bit (provider nondeterminism) and are verified by comparison against the archived
raw logs.
