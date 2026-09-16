# Final Submission Checklist — LegacyCRM-Bench → IEEE OJ-CS

Verdict source of truth: `SUBMISSION_READINESS_REPORT.md`. Do not submit while any REQUIRED
box is unchecked.

## Evidence (REQUIRED)
- [x] B1: Protocol P0 (C5 transpiler), P1–P3 (C1–C4) executed with authorization (2026-09-01/02); raw outputs +
      SHA-256 manifests archived; results in `05_results/model_runs/`
- [x] Sandbox implemented and probe-verified before first model run (Amendment A1; 7/7 checks)
- [x] `runner/redact_failures.py` implemented + automated leakage scan (ran in P3)
- [x] Frozen per-test tag map reviewed and committed (`05_results/test_tags.csv`, 521 rows)
- [x] Results/Ablation/Failure sections regenerated from model-run data; abstract updated to
      report executed findings only (manuscript v0.3)
- [x] Second full internal review cycle after results exist (2026-09-02; 31/31 numbers independently verified); ISSUE_REGISTER shows no
      unresolved Critical/Major
- [x] Independent re-derivation audit completed and archived (an external third-party reviewer, an industry firm, signed 2026-09-15; 5/5 Confirmed)
- [x] Second-platform reproduction log archived (Linux CI run 35020703092; continuous on every push)

## Formatting (REQUIRED)
- [x] B3: Ported to official IEEE Open Journals template (ieeetj.cls; v2/, 10 of 12 pages)
      (margins/type sizes untouched); confirm ≤12 double-column pages
- [x] Removed in the canonical submission manuscript (v2 has no watermark/draft strings; v1 retains them by design as the internal archive copy),
      placeholder author block, bracketed placeholders in Data Availability/Repro sections
- [x] Figures: vector PDF (F1); to be uploaded individually at the portal
      (PS/EPS/PDF/PNG/TIF) per CFP
- [x] Abstract ≤250 words (200 as submitted; within the template's stated 150–250), no refs/equations; 5 index terms
- [x] References: IEEE style, generated solely from primary-source-verified rows (the optional IEEE Reference Preparation Assistant was not run); every entry still
      matches REFERENCE_VERIFICATION.csv

## People & policy (REQUIRED)
- [x] B2: Author, affiliation, registered ORCID, corresponding author (single author; attested 2026-09-15);
      AUTHOR_CONTRIBUTIONS.md completed (CRediT); COI + funding statements
- [x] AI-use disclosure approved by the author (2026-09-15) and placed in the Acknowledgment
      (AI_USE_DISCLOSURE.md is the source text); no AI listed as author
- [x] B5: dispositioned 2026-09-16 (EiC Song Guo sourced; abstract range from official template; rest moot at our parameters) — see OJCS_CURRENT_REQUIREMENTS.md; original items:
      template class, AI-disclosure form fields (see OJCS_CURRENT_REQUIREMENTS.md UNVERIFIED)
- [x] B9: plan recorded — standard APC at acceptance with IEEE Senior Member discount; re-verify price at invoice (waiver route known);
      re-verify APC list before submission

## Artifact (REQUIRED)
- [x] B4: Public repository (github.com/chitralabs/legacycrm-bench) + Zenodo DOI 10.5281/zenodo.22777518; URLs inserted in
      manuscript + DATA_CODE_AVAILABILITY.md; release per RELEASE_MANIFEST.md
- [x] Checksums verified 2026-09-16 (model_runs SHA256SUMS: all OK)
- [x] Credential-pattern scan clean (re-run 2026-09-16: no hits)

## Submission mechanics
- [ ] Submit via IEEE Author Portal: https://ieee.atyponrex.com/journal/oj-cs
- [x] Cover letter finalized (executed-results paragraph + signature block in place; no placeholders remain
      summary)
- [x] Supplementary ZIP built (v2/10_submission_package/supplementary.zip, README with sizes)
