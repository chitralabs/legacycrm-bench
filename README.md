# LegacyCRM-Bench

**A reproducible benchmark for evaluating whether LLM-assisted migration preserves the
behavior of enterprise CRM customizations** — validation rules, workflow automations, legacy
scripts, role-based access controls, integrations, batch processing, audit logging,
referential integrity, business rules, and configuration — including their security
semantics.

Companion artifact for the manuscript *"LegacyCRM-Bench: A Reproducible Benchmark for
Evaluating LLM-Assisted Migration of Enterprise CRM Customizations"* (C. Ganesan, prepared
for IEEE Open Journal of the Computer Society; under preparation for submission).

## Highlights

- **36 migration cases / 12 categories / 521 executable acceptance tests** over a fictional,
  fully documented legacy CRM ("Meridian CRM 4.2") — 100% synthetic, no proprietary or
  personal data by construction.
- **Instrument validated end to end**: reference solutions 521/521; empty-solution control
  0/521; mutation audit loop 92.3% → 97.0% kill rate with every surviving mutant classified.
- **Deterministic no-LLM transpiler control**: solves 11/36 cases, bounding the
  LLM-attributable signal.
- **Fully executed, sandboxed, budget-capped evaluation**: 3 commercial model tiers × 4
  conditions × 5 runs (1,980 generations, zero infrastructure errors); every raw response
  archived with SHA-256 manifests; every reported number machine-generated from the raw logs.

## Layout

- `v1/` — the complete evidence archive: benchmark dataset (`02_benchmark_dataset/`),
  harness/runner/analysis code (`03_source_code/`), frozen protocol + amendments
  (`04_experiments/`), raw results (`05_results/`), generated tables/figures, manuscript
  sources, and the full internal review audit incl. the 30-claim claim–evidence ledger
  (`09_peer_review_audit/`).
- `v2/` — the manuscript on the official IEEE Open Journals template.

## Reproduce

See `v1/08_supplementary_material/REPRODUCTION_GUIDE.md`. Offline validation (structure,
reference/null, mutation, C5 transpiler, sandbox probe) is fully rerunnable; model-run
analysis re-derives all tables from the archived raw logs (checksums provided).

## Contamination notice

Released **2026-09-02**. All artifacts (including reference solutions and tests) are public
from this date; evaluations of models trained after it may be contaminated. See
`v1/02_benchmark_dataset/DATASET_CARD.md`.

## License

Code: MIT (`v1/03_source_code/LICENSE`). Data & specifications: CC BY 4.0
(`v1/02_benchmark_dataset/LICENSE-DATA.txt`).
