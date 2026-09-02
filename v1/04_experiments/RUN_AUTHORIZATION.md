# Run Authorization Record

- **Date:** 2026-09-01
- **Authorized by:** project owner (meij2eescholar@gmail.com), via interactive session prompt
- **Scope:** paid API calls for the LegacyCRM-Bench evaluation experiments per
  STUDY_PROTOCOL.md v1.0 + Amendment A1 and EXPERIMENT_PLAN.md (phases P0–P3)
- **Hard budget cap:** **$150.00 USD** — the runner must track cumulative estimated spend from
  provider usage fields and refuse to issue a call once the cap would be exceeded
- **Sequencing condition:** P1 pilot first; main phases proceed only after pilot inspection
- **Pre-run gates (Amendment A1):** sandbox implemented and probe-verified; sanitized case
  copies; frozen reviewed test-tag map; prices re-verified with retrieval date; exact token
  counts via provider count_tokens
- **Credential rule:** API keys are read from the environment at call time only; never
  written to any file in this repository; the runner startup scans the repo for key patterns
  and aborts if any are found

## Approval of dry-run estimate — 2026-09-01

The project owner reviewed 00_project_admin/OPENAI_COST_ESTIMATE.md and approved, via the
interactive session prompt: P1 pilot (≈$0.30–2.60) followed automatically by P2+P3
(≈$60–65 central scenario) under the standing $150 hard cap and the pre-committed descoping
rule (if the pilot lands in the HIGH output regime, reduce k=5→3 and/or drop C3 for sol and
log an amendment before P2). Slate: OpenAI-only per Amendment A3.
