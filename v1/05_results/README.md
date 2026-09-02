# 05_results — machine-generated results only

Every file here is produced by a script in `03_source_code/` from executed runs. Nothing in
this directory is hand-written or hand-edited. Regeneration commands:
`08_supplementary_material/REPRODUCTION_GUIDE.md`.

| File | Producer | What it is |
|---|---|---|
| reference_validation.jsonl | harness/run_all.py --solution reference | Ground-truth validation: acceptance tests vs. reference solutions |
| null_baseline.jsonl | harness/run_all.py --solution null | Discriminative-power control: empty solutions |
| mutation_results.jsonl | harness/mutation_check.py | Test sensitivity to seeded reference mutations |
| input_size_measurements.csv | analysis/measure_inputs.py | Prompt payload sizes for cost projection |
| model_runs/*.jsonl | runner/run_experiment.py | Executed model-run results (P1 pilot, P2 main, P3 repair; SHA256SUMS inside) — append-only, never hand-edited |
| c5_transpiler_baseline.jsonl | runner/transpiler_c5.py | Deterministic no-LLM baseline results (11 attempted cases + skipped list) |
| test_tags.csv (+ draft) | analysis/tag_tests.py + review | Frozen per-test property-class map (521 rows) |
| sandbox_probe_ok.json | runner/probe.py | Sandbox verification marker (7/7 checks) |
