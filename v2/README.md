# LegacyCRM-Bench — v2 (submission candidate on the official IEEE Open Journals template)

Created 2026-09-02. **v2 is the upload-facing packaging of the work; v1 remains the complete,
authoritative evidence archive** (benchmark, raw logs, analysis pipeline, review audit,
claim–evidence ledger). Nothing scientific differs between v1 and v2: the v2 manuscript body
is byte-derived from `v1/07_manuscript` v0.3 (post review-cycle-2, all numbers independently
verified 31/31); only the front matter was ported to the official class.

## Contents

- `07_manuscript/` — `LegacyCRM_Bench_OJCS_v2.tex` on the official `ieeetj.cls` (from the
  IEEE Template Selector zip supplied by the author), compiled PDF (10 pp of the 12-page
  limit), `refs.bib`, `generated/` table+macro inputs, `figures/`, and the pristine
  `template_reference.tex`.
- `10_submission_package/` — cover letter, author contribution statement, AI-use disclosure,
  data/code availability, release manifest, final checklist, claim–evidence ledger snapshot,
  and the compiled PDF.

## Regeneration rule

All quantitative content flows from v1's pipeline. To refresh after any change to raw
results: run the v1 analysis scripts (see `v1/08_supplementary_material/REPRODUCTION_GUIDE.md`),
then re-copy `v1/07_manuscript/generated/*.tex` and `figures/F1_instrument_validation.pdf`
into `v2/07_manuscript/` and recompile with `tectonic LegacyCRM_Bench_OJCS_v2.tex`.

## Status (see v1/10_submission_package/SUBMISSION_READINESS_REPORT.md for the ledger of record)

Resolved by v2: **B3** (official-template port; compiles clean, 10/12 pages). Still open
before upload: B4 (public repo + archival DOI — placeholders remain in the Data Availability
Statement), B5 (five journal-fact confirmations), B7 (independent ground-truth
re-derivation sample), B2/B8 final sign-off tick-boxes, B9 (APC decision). The v2 PDF
carries no draft watermark because the evidence is complete; it must still not be uploaded
until those items close.
