# EVIDENCE REQUIRED before a results-bearing manuscript can exist

> **STATUS UPDATE 2026-09-02:** E1–E6 are now SATISFIED by executed runs (P1–P3 + C5 under
> the frozen protocol, $33.59 metered, zero infra errors; see 05_results/model_runs/ and the
> ledger claims C019–C030). E7 was satisfied on 2026-09-01 (mutant triage + gap fixes).
> Remaining: E8 (authors/ORCIDs), E9 (official template compile), E10 (journal-fact
> confirmations) — all human-action blockers. The section below is retained as the original
> pre-run record.

Status 2026-09-01. The benchmark instrument exists and is validated (see `05_results/`), but the
paper's central empirical section — how LLM-based migration systems actually perform — has **no
evidence yet**. Under integrity rule 5, the current manuscript draft is watermarked DRAFT and
the Results section reports only instrument-validation results, explicitly stating that model
evaluation has not been run.

## Missing evidence and how to obtain it

| # | Missing evidence | Required action | Where it will live |
|---|---|---|---|
| E1 | Model performance under C1–C3 (RQ1–RQ3) | Authorize budget; implement runner; execute P1/P2 per EXPERIMENT_PLAN.md | 04_experiments/raw_outputs/, 05_results/model_runs/ |
| E2 | Agentic repair results (C4) | Implement redaction + loop; execute P3 | same |
| E3 | Run-to-run consistency (RQ4) | k=5 runs in P2/P3 | same |
| E4 | Exact token/cost/latency figures | Provider usage fields captured by runner; price sheet archived on run day | 05_results/cost_latency.csv |
| E5 | Statistical comparisons with CIs | Implement analysis/model_analysis.py; run on E1–E3 outputs | 05_results/, 06_figures_tables/ |
| E6 | Test→property-class tag map (frozen) | Run analysis/tag_tests.py + manual review | 05_results/test_tags.csv |
| E7 | Surviving-mutant triage | Manually classify each surviving mutant (equivalent vs test gap); fix test gaps | 09_peer_review_audit/mutant_triage.md |
| E8 | Author list, ORCIDs, contributions | Human authors complete AUTHORSHIP_ORCID_CHECKLIST.md | 00_project_admin/, 10_submission_package/ |
| E9 | Official OJ-CS template compile | Download IEEE Open Journals template; compile manuscript; verify 12-page fit | 07_manuscript/ |
| E10 | Unverified journal facts | Confirm items in OJCS_CURRENT_REQUIREMENTS.md "UNVERIFIED" section with the journal | 00_project_admin/ |

None of E1–E5 may be approximated, estimated, or simulated. If runs are not authorized, the
paper cannot honestly be submitted as an evaluation paper; the fallback framing (benchmark +
instrument-validation only) would itself need editor pre-checking against OJ-CS scope and is
NOT currently recommended without at least one executed model condition.
