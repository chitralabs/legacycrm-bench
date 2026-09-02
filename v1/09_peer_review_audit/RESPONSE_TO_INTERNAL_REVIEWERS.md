# Response to Internal Reviewers (cycle 1, 2026-09-01)

Eight persona reviews produced 85 issues (+1 self-reported): 6 Critical, 29 Major, 40 Minor,
11 Editorial. Every issue is dispositioned in `ISSUE_REGISTER.csv` with evidence pointers.
Outcome: **45 RESOLVED, 24 PARTIALLY RESOLVED, 9 OPEN-BLOCKER, 5 OPEN-DEFERRED, 3 ACCEPTED.**
Nothing was "resolved" by inventing evidence; open items are disclosed, not hidden.

## Major actions taken this cycle (each verifiable)

1. **Mutation-triage audit loop executed end-to-end** (BM-11, SE-04, AD-08, ED). All 28
   surviving mutants triaged with empirical verification (9 equivalent, 2 out-of-contract,
   17 genuine test gaps — including an untested RBAC administrator path). All 17 gaps closed
   with hand-derived tests (16 new tests, 12 cases); every added test verified to kill its
   target mutant; full pipeline re-run: reference 521/521, null 0/521, kill rate 92.3% → 97.0%
   (Wilson 95% CI [94.7, 98.3]); the 11 remaining survivors are exactly the triaged
   non-actionable set. Evidence: `mutant_triage.md`, GROUND_TRUTH addenda, re-run JSONLs.
2. **Security posture of future runs** (SP-01/02, ST-03): Protocol Amendment A1 mandates
   sandboxed, network-denied, environment-scrubbed candidate execution against sanitized case
   copies (no oracle files); harness timeout no longer crashes the batch (infra_error
   disposition). Implementation is an explicit P1 release gate.
3. **Statistics protocol hardened** (ST-01/04/05/06, BM-09/10): frozen unit-of-analysis rule,
   temp-0/seed clarification, infra-error re-run rule, detectable-effect bound, descriptive
   caveats moved to the tables.
4. **Circularity and slate** (AD-05, BM-07): authoring-vendor conflict disclosed in Threats;
   protocol requires ≥2 providers incl. a non-authoring vendor; cost doc corrected.
5. **LLM-necessity control added** (AD-02): condition C5, a deterministic rule-based
   transpiler baseline, added to the protocol (execution pending with the rest).
6. **Spec/artifact contradictions fixed** (CD-02/04/05/06/09, AD-07): team-resolution rule,
   owner-role quirk, no-currency-conversion rule, ROLE_PERM correction, rounding rule
   promoted to the spec, comment/boundary mismatch fixed in all copies; affected cases
   re-verified against references.
7. **Presentation** (PR-*): figure regenerated un-clipped at double-column width and made
   self-contained; bibliography misattribution fixed ("and others"), page ranges corrected;
   abstract rewritten (195 words, no abbreviations, 5 keywords); acronyms defined;
   seed-row count macro-generated; universal claims qualified or mechanically enforced
   (validator now AST-counts tests).
8. **Reproducibility** (ST-07, SE-09, BM-13): non-destructive reproduction guide with diff
   step; SHA-256 checksums for raw results; release manifest with hygiene exclusions.

## What was NOT fixed (and why)

- **No model results (ED-001/BM-01/AD-01)** — cannot be fixed without authorized, paid,
  sandboxed runs; this is blocker B1 and the reason the verdict below is NOT READY.
- **Official template port, authors/ORCIDs, public repo+DOI, journal-fact confirmations** —
  require human/browser actions (B2–B5).
- Items deferred to benchmark v0.2 (data-deliverable mutation, RBC NONE-scope rows, unused
  DSL surface, incomplete-spec task tier) are disclosed in the manuscript's Threats or
  Limitations rather than silently dropped.

A second full review cycle is required after B1 experiments run (per the fix-and-review rule);
this response covers cycle 1 only.


# Response to Internal Reviewers (cycle 2, 2026-09-02)

Cycle 2 ran after the frozen protocol was fully executed: an adversarial verifier that
independently recomputed every number from the raw JSONLs (**31/31 match, 0 mismatches**;
`CYCLE2_ADVERSARIAL_VERIFICATION.md`) and an editorial/presentation reviewer whose desk
update reads: *"I would now send it to review once the admin items are fixed."* Cycle 2
produced 42 issues (13 adversarial, 29 editorial): 1 Critical (the deliberate DRAFT/admin
state), 12 Major, 19 Minor, 10 Editorial.

Actions: every substantive prose defect was fixed the same day — the stale results-pending
sentences removed; all "current/2026 frontier models" generalizations rescoped to the
evaluated family; the causal "induces" hedged with an explicit
reproducible-pattern-not-tested-effect statement; the pass^5 tier claim scoped to C1–C3 with
the C3 mid–small tie named; RQ2 answered in Results from the frozen tag map; the Threats/CI
contradiction removed; Figure 1 cited; the checklist quotation made verbatim; failure
accounting extended to the 4 scattered small-tier failures; Wilson bounds regenerated at
higher precision; the bibliography note-field capitalization protected; contribution (5)
added; and 13 stale supporting documents refreshed (readiness report, blockers, dataset
card, reproduction guide, availability/disclosure/checklist/cover-letter, plan run-log,
READMEs, ledger rows C002/C010/C030, cycle-1 register rows). Register state after cycle 2:
128 issues, 91 RESOLVED, 24 PARTIALLY RESOLVED, 2 ACCEPTED, 5 OPEN-DEFERRED (v0.2
disclosures), 6 OPEN-BLOCKER — every open Critical/Major is an administrative human-action
item (authors/ORCIDs, official template, draft state).
