# Submission Blockers (authoritative list; details in SUBMISSION_READINESS_REPORT.md)

Status: 2026-09-02 (post review-cycle 2). Verdict: **NOT READY FOR SUBMISSION** —
remaining blockers are administrative/human-action only; scientific content complete and
independently verified (31/31 numeric checks).

| # | Severity | Blocker | Required evidence/action | Affected file(s) |
|---|---|---|---|---|
| B1 | CLOSED 2026-09-02 | Frozen protocol fully executed (pilot + P2 + P3 + C5; 1,980 generations, $33.59, zero infra errors); results independently verified 31/31 and reported in manuscript v0.3; review cycle 2 complete | — | 05_results/model_runs/; 07_manuscript |
| B2 | NEARLY CLOSED | Author details integrated 2026-09-02 (C. Ganesan, ORCID 0009-0009-1305-1724, UT Austin PGP AI/ML; bio + contributions + cover-letter signature done). Residual: final-approval and COI tick-boxes at submission | 00_project_admin/AUTHORSHIP_ORCID_CHECKLIST.md |
| B3 | CLOSED 2026-09-02 | Ported to official ieeetj.cls (author-supplied zip); 10/12 pages; submission candidate lives in ../../v2/ | — | v2/07_manuscript/ |
| B4 | PARTIALLY CLOSED | Repo LIVE: github.com/chitralabs/legacycrm-bench (v0.1, 2026-09-02); URL in manuscripts. Remaining: archival DOI + second-platform reproduction log | DOI + reproduction | DATA_CODE_AVAILABILITY.md |
| B5 | MAJOR | Unverified journal facts (page-limit hardness, abstract limit, EiC, template class, AI-form field) | Confirm via official pages/contacts listed in the audit | 00_project_admin/OJCS_CURRENT_REQUIREMENTS.md |
| B6 | CLOSED | Amendment A1 pre-run gates implemented and probe-verified 2026-09-01 (sandbox, sanitized copies, redaction+leakage scan, frozen tag map, capped runner, mock e2e 36/36) | — | 03_source_code/runner/ |
| B7 | MAJOR | Independent re-derivation audit of ground-truth sample (reviewer BM-02) outstanding | Independent human re-derivation of a case sample; archive | 09_peer_review_audit/ |
| B8 | MINOR | Cover letter placeholders; author sign-off on AI-use disclosure | Finalize after B1/B2 | COVER_LETTER_DRAFT.md; AI_USE_DISCLOSURE.md |
| B9 | MINOR | APC funding/waiver decision ($2,160 list 2026; 20% CS-member discount; waivers pubs-waivers@computer.org) | Author decision; re-verify APC before submission | FINAL_SUBMISSION_CHECKLIST.md |

Resolution rule: a blocker closes only with real evidence (executed runs, completed
checklists, verified pages) — never by weakening the integrity rules.
