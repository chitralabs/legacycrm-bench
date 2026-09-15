# Submission Readiness Report — LegacyCRM-Bench (IEEE OJ-CS)

**Date:** 2026-09-02 (supersedes 2026-09-01; prior version archived) ·
**Verdict: NOT READY FOR SUBMISSION**

The verdict follows the project's decision rule: ready only when all mandatory evidence,
experiments, references, formatting, disclosures, and reproducibility materials are complete.
The **scientific content is now complete and twice-reviewed**; what remains is exclusively
administrative and requires the human authors. The cycle-2 editor persona's assessment:
*would send to peer review once the administrative items are fixed.* No guarantee of
acceptance is implied.

## Complete and verified (evidence chain: 30-claim ledger, all VERIFIED)

| Item | Evidence |
|---|---|
| Benchmark: 36 cases, 12 categories, 521 tests; validator green | `02_benchmark_dataset/`, T1 |
| Instrument validation: reference 521/521; null 0/521; mutation audit loop 92.3%→97.0% kill (CI [94.7, 98.3]) with all 28 survivors triaged and 17 test gaps closed | `05_results/`, `mutant_triage.md` |
| C5 deterministic transpiler control (no LLM): solves 11/36; bounds LLM-attributable signal | `c5_transpiler_baseline.jsonl` |
| **Frozen protocol fully executed**: pilot + P2 (3 OpenAI tiers × C1–C3 × 5 runs) + P3 (C4 repair, 2 tiers) = 1,980 protocol generations + 11 repairs; zero infra errors; $33.59 of $150 cap | `05_results/model_runs/` + SHA256SUMS, `spend_ledger.json` |
| Security of runs: sandbox probe 7/7 (network denied, env scrubbed, oracle+credential files unreachable); mock pipeline control 36/36; automated redaction leakage scan | `runner/probe.py`, `MOCK_full_pipeline.jsonl` |
| Findings: near-ceiling case level; pass^5 separates tiers (0.889→1.000); 31 single-shot failures on quirk oracles; checklist-associated access-narrowing regression; C4 repairs all failures | M1–M5 tables; manuscript v0.3 |
| **Independent cycle-2 verification: 31/31 recomputed numbers match raw logs; 0 mismatches** | `CYCLE2_ADVERSARIAL_VERIFICATION.md` |
| Two full review cycles: 128 issues — 91 resolved, 24 partially, 2 accepted, 5 deferred-with-disclosure; no open Critical/Major beyond the administrative blockers below | `ISSUE_REGISTER.csv`, response memos |
| 38 verified references; bibliography generated only from verified rows; protected rendering | `REFERENCE_VERIFICATION.csv`, `refs.bib` |
| Manuscript v0.3: 8 pp (≤12), 200-word abstract, headline numbers macro-generated and independently audited, compiles clean | `07_manuscript/` |

## Remaining blockers (all require the human authors)

| # | Severity | Blocker | Required action |
|---|---|---|---|
| B2 | CLOSED 2026-09-15 | Author details integrated 2026-09-02; final-approval and no-COI attestations confirmed by the author in session 2026-09-15 | — |
| B3 | CLOSED 2026-09-02 | Ported to the official IEEE Open Journals class (ieeetj.cls, author-supplied Template Selector zip); compiles clean at 10 of 12 pages; see ../../v2/ | — |
| B4 | CLOSED 2026-09-15 | Public repo LIVE since 2026-09-02: github.com/chitralabs/legacycrm-bench (tag v0.1, clean credential scan, URL in both manuscripts). CLOSED 2026-09-15: repo live + Linux CI reproduction (run 35020703092) + Zenodo archival DOI 10.5281/zenodo.22777518 minted via the author's account and inserted into both manuscripts |
| B5 | MAJOR | Five unverified journal facts (page-limit hardness, abstract limit, EiC, template class, AI-form field) | Confirm via pages/contacts in `OJCS_CURRENT_REQUIREMENTS.md` §UNVERIFIED |
| B7 | MAJOR | Independent human re-derivation audit of a ground-truth sample (reviewer BM-02) | Sample-based re-derivation; archive in `09_peer_review_audit/` |
| B8 | CLOSED 2026-09-15 | Cover letter + AI-use disclosure complete; author sign-off recorded | — |
| B9 | MINOR | APC decision ($2,160 list 2026; CS-member discount; waivers pubs-waivers@computer.org) | Author decision; re-verify APC |

Closed since the last report: **B1** (evaluation executed, independently verified, reported;
review cycle 2 complete) and **B6** (all Amendment A1 gates implemented and probe-verified).

## Honesty notes

- The DRAFT watermark stays on the PDF until B2/B3 close.
- Disclosed limitations stand: single-vendor slate (Amendment A3), 36-case pilot scale,
  near-ceiling case-level scores with underpowered condition contrasts (flagged, never tested
  to verdicts), post-release contamination window, and one self-reported process deviation
  (SELF-01: pre-fix mutation raw log overwritten before archiving).
