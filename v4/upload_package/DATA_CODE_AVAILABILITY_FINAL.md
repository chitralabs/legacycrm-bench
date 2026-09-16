# Data and Code Availability Statement

All artifacts behind every reported number are synthetic, openly licensed, and **publicly
available now**: the fictional Meridian CRM 4.2 specification and legacy artifacts, the
deterministic seed-data generator (fixed seed; byte-identical regeneration), all 36
benchmark cases with executable acceptance tests, reference solutions, and ground-truth
derivation documents, the sandboxed evaluation harness and analysis scripts, the frozen
prompts and study protocol with logged amendments, and the complete raw run logs — every
model generation and the spend ledger — with SHA-256 manifests.

- Repository: https://github.com/chitralabs/legacycrm-bench
  (repository tag `v0.1`, dated 2026-09-02; archival release `v0.1.1`, 2026-09-15)
- Permanent archive: Zenodo concept DOI **10.5281/zenodo.22777518** (resolves to the latest
  archived version); the evaluation reported in this paper corresponds to version DOI
  10.5281/zenodo.22777519.
- Licenses: MIT (code); CC BY 4.0 (data and specifications).
- Independent reproduction: the offline validation pipeline (seed determinism, case
  validation, per-test reference/null outcomes, per-mutant kill outcomes, and byte-identical
  regeneration of all tables) runs continuously on Linux in the repository's
  integration workflow; the archived first run is included in the supplementary material.
  The paid model calls themselves are not re-runnable bit-for-bit and are verified by
  comparison against the archived raw logs.

No proprietary data, confidential information, internal system data, customer records, or
employer-owned data of any kind was used. No data originating from the author's employer or
from any commercial CRM deployment appears anywhere in this work, and the manuscript was
prepared in compliance with standard employer confidentiality obligations.
