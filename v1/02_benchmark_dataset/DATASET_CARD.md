# Dataset Card — LegacyCRM-Bench v0.1 (pilot)

**Created:** 2026-09-01 · **License:** data/specs CC BY 4.0; code (harness, tests, reference
solutions, generators) MIT · **Status:** pilot instrument, fully validated; frozen-protocol
evaluation executed 2026-09-01/02 (C5 deterministic transpiler + three OpenAI model tiers
under four conditions, 1,980 sandboxed generations; raw logs in `05_results/model_runs/`).

## Summary

LegacyCRM-Bench is a benchmark of migration tasks over a fictional, fully documented legacy CRM
("Meridian CRM 4.2"). Each case pairs legacy customization artifacts (SQL schema, a validation
rule DSL, XML workflows, a BASIC-like scripting language, an RBAC matrix, integration/batch/audit
configuration) with a precise target specification and executable pytest acceptance tests that
check whether a migrated implementation preserves the documented legacy behavior, including
security semantics.

## Composition

36 cases across 12 categories (schema mapping, validation rules, workflows, legacy scripts,
RBAC, integration, batch processing, error handling, audit logging, referential integrity,
business rules, configuration modernization) × 3 difficulties. Exact counts and test totals:
`06_figures_tables/T1_benchmark_composition.csv` (machine-generated).

## Provenance and generation process

- The legacy system, its DSL semantics, and all artifacts are **synthetic**, authored for this
  benchmark on 2026-09-01. They contain no employer, customer, vendor, or proprietary material
  and no real personal data. "Meridian CRM" is fictional; resemblance to real products is
  limited to generic industry conventions.
- Seed data (716 rows across 10 entity CSVs) is generated deterministically by
  `03_source_code/generate_seed_data.py` (seed 20260901, stdlib only, fictional name lists);
  regeneration is byte-identical.
- Cases were authored by the project using a generative-AI coding assistant (Claude, Anthropic)
  under human direction, against the frozen written semantics in
  `legacy_system/SYSTEM_OVERVIEW.md`. Every non-obvious expected value carries a written
  hand-derivation in the case's `GROUND_TRUTH.md`. Ground truth is defined by the documented
  semantics + executable tests, not by any LLM's opinion.
- Validation of the instrument (executed, results in `05_results/`): reference solutions pass
  100% of tests; an empty (null) solution passes 0; AST-level mutation analysis measures test
  sensitivity (`05_results/mutation_results.jsonl`).

## Intended use

Evaluating whether LLM-assisted migration pipelines preserve legacy CRM customization behavior.
NOT a measure of: real-vendor migration difficulty, production readiness, developer
productivity, or agent task-completion ability in live CRMs (see CRMArena/CRMArena-Pro for that).

## Known limitations

The modeled system is **single-tenant**: cross-tenant isolation, a first-order security
concern in multi-tenant CRM platforms, is entirely out of scope of the security oracles.

Synthetic and simplified relative to real enterprise systems; pilot scale (36 cases; 3 per
category) limits statistical power for category-level conclusions; single documented semantics
(no vendor variance); reference solutions are released, so future model training may be
contaminated (release is dated; held-out variants are future work); tests, while
mutation-checked, cannot guarantee full behavioral coverage.

## Distribution & contamination note

Public release intended with the paper. Anything released on/after 2026-09-01 may enter future
training corpora; evaluation results on models trained after release must note this.
