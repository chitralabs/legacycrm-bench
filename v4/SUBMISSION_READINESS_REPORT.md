# Submission Readiness Report — LegacyCRM-Bench v4 (IEEE OJ-CS)

**Date:** 2026-09-16 · **Verdict: READY FOR AUTHOR CONFIRMATION**

The scientific package is complete, corrected, and validated; the manuscript passes
technical and visual inspection; every number and link is verified. The verdict is **not**
"READY FOR SUBMISSION" because five decisions belong to the author alone and were
deliberately not made on her behalf (list below). No guarantee of acceptance is implied.

## Evidence base (unchanged science, corrected characterizations)

| Item | Status |
|---|---|
| Benchmark: 36 cases / 12 categories / 521 tests; validator green | verified (T1; CI-reproduced) |
| Instrument: reference 521/521; null 0/521; mutation audit 92.3%→97.0% kill (CI [94.7, 98.3]); all survivors triaged | verified (raw logs + triage) |
| C5 deterministic transpiler control: 11/36 solvable without any LLM | verified |
| Executed protocol: 1,980 generations + pilot + 11 repairs; zero infra errors; $33.59 of $150 cap | verified (SHA-256-manifested raw logs) |
| Independent numeric verification: 31/31 recomputed from raw logs, 0 mismatches (cycle 2) | verified |
| Continuous Linux reproduction of the offline pipeline (first run archived) | verified |
| References: 38, all primary-source verified; 42 DOIs/URLs re-checked 2026-09-16 (4 ACM DOIs via Crossref registry) | verified |
| Claim–evidence ledger: **34 rows**, all VERIFIED; C034 wording corrected per Phase-3 audit | verified |
| Ground-truth spot-check: AI-assisted spec-only derivation, 5/5 concordant, mechanically re-verified, human-reviewed and signed | truthfully characterized (Phase 3) |
| Manuscript: **10 pages** of 12; abstract **198 words** (100–200 gate met; ≤250 IEEE cap); 5 index terms; official ieeetj template; figure fonts embedded (no Type 3); all pages visually inspected | verified |
| Public artifact: repo (tag v0.1 / archival release v0.1.1) + Zenodo DOI 10.5281/zenodo.22777518 | live, links verified |

## Technical validation (Phase 8)

Clean compile (tectonic/XeTeX); zero undefined citations or references; overfull-vbox
warnings are float-page stretch only — page-by-page visual render shows no clipped content;
fonts embedded throughout, figure regenerated without Type 3 fonts; supplementary
ZIP integrity-tested (19 files, size inventory regenerated); SHA-256 manifest covers every
v4 file; credential-pattern scan clean. Not performed (account-gated web tools, disclosed):
IEEE hosted LaTeX Analyzer and PDF eXpress-style checker.

## Material findings from the fresh requirements verification (2026-09-16)

- **No revision round**: the CS Peer Review Schedules page states OJ-CS uses an expedited
  single-anonymous process with *no revision option* — the uploaded version must be final.
  This raises the value of the two completed internal review cycles and the author's final
  read-through (item 6 below).
- **Abstract limits conflict across official sources** (250 generic / 150–250 style manual /
  100–200 CS-wide); the manuscript's **198 words satisfies all three** simultaneously.
- Page limit: 12 pages regular (a 20-page survey tier now also exists); we are at 10.
- Biography/photo: not required at initial submission; the template's biography is retained
  (permitted, and part of the official template layout).
- Full sourced detail: `OJCS_CURRENT_REQUIREMENTS_VERIFIED.md`.

## Author confirmations required before submission (the only open items)

1. **Affiliation** — confirm "Independent Researcher, Dallas, TX, USA" as typeset, or
   document entitlement to the UT Austin program affiliation
   (`AUTHOR_AFFILIATION_CONFIRMATION_REQUIRED.md`).
2. **Employer clearance** — confirm completed or not applicable.
3. **IEEE member grade** — confirm active Senior Member record to restore the byline grade,
   or leave it out.
4. **Zenodo creator metadata** — perform the 3-minute fix
   (`ZENODO_METADATA_UPDATE_INSTRUCTIONS.md`) or accept the current record knowingly.
5. **Phase-3 characterization** — read and accept
   (`HUMAN_VERIFICATION_INTEGRITY_AUDIT.md`).
6. **Final read-through** of `manuscript/LegacyCRM_Bench_OJCS_submission_v4.pdf` and
   approval of the exact uploaded version (IEEE authorship responsibility).

When all six are confirmed, the package qualifies for READY FOR SUBMISSION with no further
assistant-side work required; upload per `PORTAL_SUBMISSION_STEPS.md`.

## Residual risks reviewers may raise (disclosed in the manuscript, not fixable by editing)

Single-vendor model slate; 36-case pilot scale with underpowered condition contrasts;
near-ceiling case-level scores (calibration framing); synthetic-environment construct
validity; shared-blind-spot risk from AI-assisted construction (mitigated, not removed);
post-release contamination window; C5 saturating a third of the cases.
