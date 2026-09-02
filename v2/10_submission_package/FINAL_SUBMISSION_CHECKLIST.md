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
- [ ] Second full internal review cycle after results exist; ISSUE_REGISTER shows no
      unresolved Critical/Major
- [ ] Independent re-derivation audit of a case sample (BM-02) completed and archived
- [ ] Second-platform reproduction log archived

## Formatting (REQUIRED)
- [ ] B3: Port to official IEEE Open Journals template from https://template-selector.ieee.org/
      (margins/type sizes untouched); confirm ≤12 double-column pages
- [ ] Remove: DRAFT watermark block, draft note in title, "[DRAFT ...]" strings,
      placeholder author block, bracketed placeholders in Data Availability/Repro sections
- [ ] Figures: ≥600 dpi line art / vector; self-contained paths; submitted individually
      (PS/EPS/PDF/PNG/TIF) per CFP
- [ ] Abstract ≤250 words (currently 195), no abbreviations/refs/equations; 3–5 index terms
- [ ] References: IEEE style; run IEEE Reference Preparation Assistant; every entry still
      matches REFERENCE_VERIFICATION.csv

## People & policy (REQUIRED)
- [ ] B2: Author list, affiliations, registered ORCIDs (all authors), corresponding author;
      AUTHOR_CONTRIBUTIONS.md completed (CRediT); COI + funding statements
- [ ] AI-use disclosure reviewed/approved by authors and placed in Acknowledgments
      (AI_USE_DISCLOSURE.md is the source text); no AI listed as author
- [ ] B5: Confirm with journal: hard/soft 12-page limit, OJ-CS abstract limit, current EiC,
      template class, AI-disclosure form fields (see OJCS_CURRENT_REQUIREMENTS.md UNVERIFIED)
- [ ] B9: APC plan ($2,160 list 2026; member discounts; waivers pubs-waivers@computer.org);
      re-verify APC list before submission

## Artifact (REQUIRED)
- [ ] B4: Public repository + archival DOI (Zenodo / IEEE DataPort); URLs inserted in
      manuscript + DATA_CODE_AVAILABILITY.md; release per RELEASE_MANIFEST.md
- [ ] `shasum -a 256 -c 05_results/SHA256SUMS` passes on the release copy
- [ ] Credential-pattern scan of release tree is clean

## Submission mechanics
- [ ] Submit via IEEE Author Portal: https://ieee.atyponrex.com/journal/oj-cs
- [ ] Cover letter finalized (COVER_LETTER_DRAFT.md placeholders replaced with executed-results
      summary)
- [ ] Supplementary ZIP per IEEE format rules (README with sizes)
