# Second-Platform Reproduction Log

**Date:** 2026-09-15 · **Platform:** GitHub Actions `ubuntu-latest` (Linux x86_64),
Python 3.13, dependencies pinned from `03_source_code/requirements.txt` · **Run:**
https://github.com/chitralabs/legacycrm-bench/actions/runs/35020703092 (workflow
`offline-validation`, conclusion: success) — vs. the original environment
(macOS arm64, Python 3.14.2).

Independently verified on the second platform:

1. **Seed-data determinism** — regeneration produced byte-identical CSVs to the committed
   files (`git diff --exit-code`).
2. **Structural validation** — all 36 cases, 0 errors.
3. **Reference validation** — full rerun; per-test outcomes (521 tests across 36 cases)
   identical to the archived `reference_validation.jsonl`.
4. **Null-baseline control** — full rerun; 0 tests passed anywhere.
5. **Mutation analysis** — full rerun (363 mutants, cap 12/case); per-mutant kill outcomes
   identical to the archived `mutation_results.jsonl`.
6. **Analysis regeneration** — every table (T1–T3, M1–M5, disposition), every manuscript
   number macro, and the bibliography regenerate byte-identically from the archived raw logs
   (`git diff --exit-code` over `06_figures_tables`, `07_manuscript/generated`, `refs.bib`).

Out of CI scope by design: paid model calls (non-rerunnable; verified instead by per-test
comparison against archived logs above) and the sandbox probe / C5 evaluation path (requires
macOS `sandbox-exec`; verified on the original platform). The workflow runs on every push,
so this reproduction is continuous, not one-off.
