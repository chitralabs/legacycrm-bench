# Data and Code Availability Statement (draft; hosting must be completed before submission)

The complete LegacyCRM-Bench artifact — the synthetic Meridian CRM 4.2 legacy specification and
artifacts, all 36 benchmark cases with executable acceptance tests and reference solutions, the
deterministic seed-data generator, the evaluation harness, mutation-analysis and aggregation
scripts, raw result files, and the reproduction guide — is intended for public release under
MIT (code) and CC BY 4.0 (data/specifications).

**Blocker (2026-09-01):** no public repository or archival deposit exists yet. Before
submission the authors must: (1) publish the artifact to a public repository (e.g., GitHub) and
an archival service with DOI (e.g., Zenodo or IEEE DataPort, which the OJ-CS audit notes IEEE
encourages); (2) insert the concrete URLs/DOI here and in the manuscript's Data Availability
section; (3) verify the release contains no personal data or credentials (it contains none by
construction; run the release checklist in FINAL_SUBMISSION_CHECKLIST.md).

Model-evaluation raw outputs now exist (executed 2026-09-01/02): immutable per-call JSON in
`04_experiments/raw_outputs/`, per-run JSONL + SHA-256 manifests in `05_results/model_runs/`,
and the C5 transpiler baseline; all are part of the same release.
