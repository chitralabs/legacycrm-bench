# LegacyCRM-Bench — v3 (FROZEN SUBMISSION PACKAGE)

**Frozen:** 2026-09-16 · **Verdict at freeze: READY FOR SUBMISSION**
(`upload_package/SUBMISSION_READINESS_REPORT.md`; decision rule satisfied, blockers B1–B8
closed with evidence, B9/APC due at acceptance). No guarantee of acceptance is implied.

This folder is the exact upload kit. Content is frozen: the manuscript PDF is byte-identical
to the v2 compile on the official IEEE Open Journals template (`ieeetj.cls`, 10 of 12 pages);
`MANIFEST.sha256` fingerprints every file. v1/ remains the evidence archive, v2/ the
template-port workspace; if anything is ever changed, regenerate there and re-freeze a v4 —
do not edit files here.

## Upload sequence — IEEE Author Portal: https://ieee.atyponrex.com/journal/oj-cs

1. **Manuscript:** `manuscript/LegacyCRM_Bench_OJCS_submission.pdf`
   (source: `LegacyCRM_Bench_OJCS_v2.tex` + `ieeetj.cls` + `generated/` + `refs.bib`, if the
   portal requests LaTeX source).
2. **Figure (individually):** `manuscript/figures/F1_instrument_validation.pdf` (vector).
3. **Cover letter:** paste `upload_package/COVER_LETTER.md`.
4. **Supplementary material:** `upload_package/supplementary.zip` (README with sizes inside).
5. **Forms:** ORCID 0009-0009-1305-1724; single author (C. Ganesan, Senior Member, IEEE);
   AI-disclosure field → YES, per the Acknowledgment section; no conflicts of interest.
6. **At acceptance:** APC $2,160 list (2026) minus IEEE Senior Member discount; re-verify the
   current APC list at invoice; waivers via pubs-waivers@computer.org.

## Provenance anchors

- Public artifact: https://github.com/chitralabs/legacycrm-bench (tag v0.1.1)
- Archival DOI: https://doi.org/10.5281/zenodo.22777518 (concept; version 10.5281/zenodo.22777519)
- Continuous reproduction: GitHub Actions `offline-validation` (second-platform log archived)
- Evidence chain: 34-claim ledger (`upload_package/CLAIM_EVIDENCE_LEDGER.csv`), two internal
  review cycles (128 issues dispositioned), independent 31/31 numeric verification, signed
  third-party ground-truth verification (2026-09-15; signed record held in the private
  archive at v1/09_peer_review_audit/).
