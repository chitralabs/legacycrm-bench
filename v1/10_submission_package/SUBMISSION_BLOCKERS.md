# Submission Blockers (authoritative list; details in SUBMISSION_READINESS_REPORT.md)

Status: 2026-09-16. Verdict: **READY FOR SUBMISSION** — B1–B8 all CLOSED with evidence;
B9 (APC payment) falls due at acceptance. See SUBMISSION_READINESS_REPORT.md.

| # | Severity | Blocker | Required evidence/action | Affected file(s) |
|---|---|---|---|---|
| B1 | CLOSED 2026-09-02 | Frozen protocol fully executed (pilot + P2 + P3 + C5; 1,980 generations, $33.59, zero infra errors); results independently verified 31/31 and reported in manuscript v0.3; review cycle 2 complete | — | 05_results/model_runs/; 07_manuscript |
| B2 | CLOSED 2026-09-15 | Author details integrated; final-approval and no-COI attestations confirmed in session 2026-09-15 | — | 00_project_admin/AUTHORSHIP_ORCID_CHECKLIST.md |
| B3 | CLOSED 2026-09-02 | Ported to official ieeetj.cls (author-supplied zip); 10/12 pages; submission candidate lives in ../../v2/ | — | v2/07_manuscript/ |
| B4 | CLOSED 2026-09-15 | Repo LIVE: github.com/chitralabs/legacycrm-bench (v0.1, 2026-09-02); URL in manuscripts. CLOSED 2026-09-15: repo + CI reproduction + Zenodo DOI 10.5281/zenodo.22777518 (v0.1.1) inserted everywhere | — | DATA_CODE_AVAILABILITY.md |
| B5 | CLOSED 2026-09-16 | All items sourced or moot (see readiness report row) | — | 00_project_admin/OJCS_CURRENT_REQUIREMENTS.md |
| B6 | CLOSED | Amendment A1 pre-run gates implemented and probe-verified 2026-09-01 (sandbox, sanitized copies, redaction+leakage scan, frozen tag map, capped runner, mock e2e 36/36) | — | 03_source_code/runner/ |
| B7 | MAJOR | Independent re-derivation audit of ground-truth sample (reviewer BM-02) outstanding | Independent human re-derivation of a case sample; archive | 09_peer_review_audit/ |
| B8 | CLOSED 2026-09-15 | Cover letter complete; author sign-off recorded | — | COVER_LETTER_DRAFT.md |
| B9 | MINOR | APC funding/waiver decision ($2,160 list 2026; 20% CS-member discount; waivers pubs-waivers@computer.org) | Author decision; re-verify APC before submission | FINAL_SUBMISSION_CHECKLIST.md |

Resolution rule: a blocker closes only with real evidence (executed runs, completed
checklists, verified pages) — never by weakening the integrity rules.
