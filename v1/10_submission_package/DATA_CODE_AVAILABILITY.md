# Data and Code Availability Statement (draft; hosting must be completed before submission)

The complete LegacyCRM-Bench artifact — the synthetic Meridian CRM 4.2 legacy specification and
artifacts, all 36 benchmark cases with executable acceptance tests and reference solutions, the
deterministic seed-data generator, the evaluation harness, mutation-analysis and aggregation
scripts, raw result files, and the reproduction guide — is intended for public release under
MIT (code) and CC BY 4.0 (data/specifications).

**Published 2026-09-02:** https://github.com/chitralabs/legacycrm-bench (public, tag v0.1),
released per RELEASE_MANIFEST.md with a clean credential-pattern scan. Remaining before
submission: (1) archival DOI deposit (Zenodo or IEEE DataPort — requires the author's
account); (2) insert the DOI here and in the manuscript; (3) second-platform reproduction
log.

Model-evaluation raw outputs now exist (executed 2026-09-01/02): immutable per-call JSON in
`04_experiments/raw_outputs/`, per-run JSONL + SHA-256 manifests in `05_results/model_runs/`,
and the C5 transpiler baseline; all are part of the same release.
