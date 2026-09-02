# Internal Pre-Submission Review 4 — Adversarial Review (Reviewer 2)

**Persona:** External reviewer determined to reject; assumes nothing, checks everything,
credits nothing that is not executed and verified.
**Reviewed:** 2026-09-01. Full manuscript against `09_peer_review_audit/CLAIM_EVIDENCE_LEDGER.csv`,
`05_results/*`, `06_figures_tables/*`, `07_manuscript/generated/*`, `01_literature/NOVELTY_AUDIT.md`,
`04_experiments/*`, and the benchmark/harness sources.

---

## Rejection-grade summary

**Recommendation: REJECT (resubmission possible after experiments are run).**

This is a benchmark-and-evaluation paper with no evaluation. All four research questions
(RQ1–RQ4, \S5 of `LegacyCRM_Bench_OJCS_v1.tex`) are explicitly unanswered; the Results section's
own subheading is "What does not exist yet" and the Ablation section is "Planned, not
executed." What remains — 36 hand-built pytest tasks over a self-invented toy DSL, validated by
running the authors' own solutions against the authors' own tests — is competent
instrumentation, but instrumentation is not a contribution the evidence can carry into an
archival journal on its own, a conclusion the authors' *own* planning document reaches:
`04_experiments/EVIDENCE_REQUIRED.md` states the instrument-only framing "is NOT currently
recommended without at least one executed model condition." The paper also lacks the one
baseline that would justify the benchmark's existence (a deterministic transpiler), releases
its tests and reference solutions together (guaranteeing contamination of every future
evaluation it is supposed to enable), and was built with the same vendor's model family it
plans to evaluate. In fairness, the internal numeric consistency is impeccable — every figure
I recomputed matched — and the paper never claims results it does not have. It is honest. It
is also premature.

---

## A. The missing experiments (fatal)

- **No model has been run.** `EXPERIMENT_PLAN.md` status: "planned — not executed";
  `05_results/model_runs/` deliberately absent; ledger C010 documents the absence. The
  abstract's subject — "Evaluating LLM-Assisted Migration" (title!) — has zero empirical
  content. The title promises an evaluation benchmark; the paper delivers a validated test
  suite. For OJ-CS this is a scope mismatch at minimum and desk-reject material as submitted.
  **AD-01 (Critical).**
- The instrument-validation evidence (RQ0), while real, is *self-referential*: reference
  solutions written by the case authors pass tests written by the case authors (505/505,
  `05_results/reference_validation.jsonl`). The null control and mutation analysis are the
  only external legs — and the survivor triage completed during this audit
  (`09_peer_review_audit/mutant_triage.md`) *confirms* multiple TEST_GAP oracle holes,
  including in the RBAC category the paper's security claims lean on (see AD-08).

## B. Missing baselines (the benchmark cannot demonstrate its own necessity)

The legacy DSLs are small, closed, and perfectly documented (`SYSTEM_OVERVIEW.md` is ~120
lines; VRL has ~10 operators and 6 functions; the workflow XML has 3 elements). **A rule-based
deterministic transpiler — a weekend of work for the authors, who wrote the DSLs — could
plausibly saturate large parts of all twelve categories.** If it can, LLM evaluation on this
benchmark measures nothing an off-the-shelf compiler doesn't already solve; if it cannot, that
result would itself be the strongest motivation in the paper. No such baseline exists,
is planned (`STUDY_PROTOCOL.md` \S3 lists only C0 null and C1–C4 LLM conditions), or is even
discussed. The only executed control is the empty solution. A benchmark paper that cannot
say "deterministic tooling achieves X%, leaving Y% headroom for learned systems" has not
established that its task requires the systems it proposes to evaluate. **AD-02 (Major).**
Also missing: any human-expert baseline or inter-author agreement on case difficulty labels
(the easy/medium/hard rubric in `CASE_FORMAT.md` is applied by fiat, n=1 authority).

## C. Novelty: incremental assembly

Strip the honest disclaimers and what is new? Not CRM benchmarking (CRMArena/-Pro), not
access-control-aware enterprise simulation (EnterpriseBench), not execution-checked
translation (TransCoder → AlphaTrans, which already does repository-level differential
validation during migration), not migration benchmarks (PyMigBench), not mutation-validated
oracles (EvalPlus), not pass^k (τ-bench) — all conceded in \S2–\S3 and in
`01_literature/NOVELTY_AUDIT.md` ("Claims LegacyCRM-Bench must NOT make," items 1–5). The
residual claim is the *object*: configured platform behavior (rules/workflows/RBAC/audit)
rather than code or agent tasks. That is a real gap, but it is a **framing** contribution
instantiated at pilot scale (36 cases, 3 per category, one synthetic system, one target
language), with no evidence any model finds it hard, easy, or interesting. As a workshop or
registered-report artifact: fine. As an archival journal contribution: thin. **AD-03 (Major).**

## D. Data leakage and contamination

1. **Release design guarantees contamination.** Tests, reference solutions, and ground-truth
   derivations ship in one public artifact (`STUDY_PROTOCOL.md` \S7 records the decision;
   `DATASET_CARD.md` limitations). Every post-release model is presumptively trained on the
   oracles; held-out variants are "future work." The paper's own dated-release argument
   protects only the *first* evaluation — which does not exist. The benchmark's useful
   lifetime may therefore be zero. **AD-04 (Major).**
2. **Runtime oracle access.** Candidate code executes unsandboxed beside the oracle and can
   read `tests/`, `GROUND_TRUTH.md`, and `reference/` at test time (see Security review
   SP-01/SP-02, `harness/run_case.py`); the C4 "tests never shown to the model" control
   (\S7) is prompt-side only. Any future C4 number is gameable by construction. **Folded into
   AD-04.**
3. **C4 redaction is vaporware:** `runner/redact_failures.py` cited in
   `EXPERIMENT_PLAN.md` does not exist (`03_source_code/runner/` absent); its audit is a 10%
   manual sample. The manuscript's Limitations (6) says the risk "is audited but cannot be
   proven absent" — as of this draft nothing is audited because nothing is built.
4. **Vendor circularity.** The cases, tests, and reference solutions were authored with
   Claude (`DATASET_CARD.md` provenance; manuscript Acknowledgments), the cost plan prices
   only Anthropic models by name (`ESTIMATED_COSTS.md`), and the planned slate will include
   them. Evaluating a model family on oracles co-drafted by that family is a bias channel the
   paper never discusses; and the Conclusion's "hand-derived executable oracles" sits
   uncomfortably beside the disclosed AI authorship — "hand-derivable, AI-drafted,
   human-directed" is the accurate phrase, and \S Threats should name the circularity.
   **AD-05 (Major).**

## E. Unverified claims — cross-check against the ledger (the hunt)

`CLAIM_EVIDENCE_LEDGER.csv` covers C001–C014. I hunted for manuscript claims outside its
coverage and found these:

1. **"every non-obvious expected value carries a written derivation"** (\S Dataset,
   "Authoring process") — universally quantified, verified nowhere. The validator
   (`validate_cases.py`) checks only that `GROUND_TRUTH.md` exists, not that derivations
   cover the expectations; no ledger row exists. **AD-06 (Major).**
2. **"at least one negative expectation per case"** (\S Oracles, "Oracle design rules") — not
   enforced by `validate_cases.py` (no such check in the source), not in the ledger. I spot-
   verified 7 cases where it holds, but a universal claim needs a mechanical check across all
   36. **AD-06.**
3. **"The complete semantics are frozen in a specification document that is the sole
   authority for expected behavior"** (\S Dataset) — falsified by the artifact:
   SCR-01's half-up-to-cents rounding is fixed by a *script comment*, not by
   `SYSTEM_OVERVIEW.md` (which documents no storage-rounding rule); the case's own
   `GROUND_TRUTH.md` admits "The script comment fixes rounding." Small, but it is a
   false universal in the methods section. **AD-07 (Minor).**
4. **Surviving-mutant disclosure is now behind the evidence.** The triage
   (`09_peer_review_audit/mutant_triage.md`, completed during this audit cycle per
   `EVIDENCE_REQUIRED.md` E7) classifies survivors and finds confirmed TEST_GAPs — including
   RBC-01 surviving an ADMIN-override mutation because *no RBC-01 test uses an ADMIN user*.
   The manuscript (\S Failure) still frames survivors as "equivalent mutant or test gap" to
   be determined, discloses no gap findings, and the gaps themselves are unfixed; the
   92.3% kill rate is quoted without noting that several survivors are known oracle holes in
   the security category. **AD-08 (Minor, was: triage absent; now: findings undisclosed and
   unfixed).**
5. **"the risk is concentrated in this layer"** (\S1) — empirical assertion, no citation, no
   ledger row. **AD-13 (Minor).**
6. Related-work characterizations (e.g., τ-bench's pass^k, WorkArena on live ServiceNow) rest
   on `PRIOR_WORK_NOTES.md`; ledger C008 verifies that references exist and match primary
   sources, not that each comparative sentence is accurate. Adequate for most venues, but the
   ledger's own standard ("every reported number traces to...") is not met by these
   qualitative claims. **AD-11 (Minor).**

## F. Numbers: text vs. tables vs. raw data (checked, mostly clean)

I recomputed every quantitative claim I could reach. To be explicit about what did **not**
fail: `\NumCases`=36, `\NumTests`=505, 505/505 reference, 0/505 null, 363 mutants, 335
killed, 92.3%, 28 survivors (`generated/numbers.tex`) all match
`T1_benchmark_composition.csv`, `T2_groundtruth_validation.csv`, `T3_mutation_sensitivity.csv`,
`surviving_mutants.csv` (28 rows), and the JSONL files; per-category sums foot to totals; the
716-row seed claim matches an independent row count of `seed_data/*.csv`; per-case test counts
(11–20) sum to the per-category totals; 38 bib entries match 38 verification rows. The
generation pipeline works. No fabricated or inconsistent number was found — the paper's
integrity machinery does what it says. (Recorded here so this review cannot be accused of
inventing problems.)

What I *can* attack: **the numbers that exist answer only RQ0**, and one number is an
unaudited heuristic presented in the planning chain — the 91,850-token C1 estimate (ledger
C011) is chars÷4 and properly labeled, but the price basis in `ESTIMATED_COSTS.md` is
"cached 2026-06-24 — RE-VERIFY," i.e., explicitly unverified at draft date. It is not in the
manuscript, so no manuscript defect — but nothing from that file may migrate into the paper
as-is.

## G. Irreproducible / dangling procedure references

- The manuscript's header comment (line 2) directs readers to
  `10_submission_package/SUBMISSION_READINESS_REPORT.md` — **which does not exist** (the
  directory contains only AI_USE_DISCLOSURE, COVER_LETTER_DRAFT, DATA_CODE_AVAILABILITY).
  `README.md` calls the same missing file "the authoritative readiness verdict," and
  `FINAL_SUBMISSION_CHECKLIST.md` (cited in `EXPERIMENT_PLAN.md` and
  `DATA_CODE_AVAILABILITY.md`) is also absent. The project's compliance trail has holes at
  exactly the nodes it advertises. **AD-09 (Minor).**
- All executed results derive from a single machine/OS/Python (per `05_results` `_meta`:
  macOS 15.7.3 arm64, CPython 3.14.2); no CI, no cross-platform replication; the title's
  "Reproducible" is, today, "reproduced once, by the authors, on one laptop," with no public
  repository or DOI (Data Availability blocker). **AD-10 (Minor).**

## H. Overgeneralization scan (Discussion/Implications/Conclusion)

The hedging discipline is unusually good — \S Discussion explicitly makes "no performance
claims," and \S8's "What will NOT be claimed" is honored in the text. Residual overreach:
the title ("Enterprise CRM Customizations," "Evaluating LLM-Assisted Migration") promises
more than the toy-scale, evaluation-free content; \S Implications' "checklist of migration
hazards" framing exceeds modeled coverage (see CRM review CD-01/CD-03); \S Taxonomy's
"derived from the customization surfaces of mainstream CRM platforms" is unsupported by any
artifact (CD-03). Conclusions otherwise stay within results.

## Strongest possible negative review (as it would read)

> The authors present a 36-task pytest suite over a fictional CRM of their own design and
> report that their own solutions pass their own tests. No language model — the paper's
> stated object of study — is ever run. No deterministic baseline establishes that the tasks
> require learned systems at all. The novelty is a framing delta over CRMArena, AlphaTrans,
> PyMigBench, and EvalPlus, each of which contributes the actual techniques used. The
> release design ships oracles beside solutions, contaminating every future use; the harness
> would execute untrusted model code with no isolation; and the benchmark was co-authored by
> a model family the protocol plans to evaluate. The instrument validation is careful and the
> honesty is commendable, but a journal paper requires evidence, and the evidence section is
> a promissory note. Reject; resubmit after executing the frozen protocol, adding a
> transpiler baseline, and sandboxing the harness.

## Issue summary (this review)

| ID | Severity | Location | Issue |
|---|---|---|---|
| AD-01 | Critical | tex \S Setup/\S Results; EXPERIMENT_PLAN.md | No LLM evaluation executed; RQ1–RQ4 unanswered; evaluation-shaped paper without evaluations |
| AD-02 | Major | STUDY_PROTOCOL.md \S3 | No deterministic/rule-based transpiler baseline; benchmark cannot demonstrate LLM-necessity or headroom |
| AD-03 | Major | tex \S2–\S3; NOVELTY_AUDIT.md | Novelty is incremental assembly; residual contribution is framing at pilot scale |
| AD-04 | Major | STUDY_PROTOCOL.md \S7; DATASET_CARD.md; harness/run_case.py | Tests+references released together (future contamination); runtime oracle access gameable; C4 redaction unimplemented |
| AD-05 | Major | DATASET_CARD.md provenance; ESTIMATED_COSTS.md; tex Conclusion | Vendor circularity (Claude-authored oracles, Anthropic-model evaluation plan) undiscussed; "hand-derived" phrasing strains disclosure |
| AD-06 | Major | tex \S Dataset/\S Oracles; validate_cases.py; CLAIM_EVIDENCE_LEDGER.csv | Universal claims ("every non-obvious value derived", "≥1 negative test per case") mechanically unverified and outside the ledger |
| AD-07 | Minor | tex \S Dataset; SCR-01/GROUND_TRUTH.md; SYSTEM_OVERVIEW.md | "Sole authority" claim false: SCR-01 rounding semantics come from a script comment |
| AD-08 | Minor | tex \S Failure; surviving_mutants.csv; mutant_triage.md | Triage now done and confirms security-category oracle gaps; manuscript discloses none of it and gaps unfixed |
| AD-09 | Minor | tex line 2; README.md; 10_submission_package/ | Dangling references: SUBMISSION_READINESS_REPORT.md and FINAL_SUBMISSION_CHECKLIST.md do not exist |
| AD-10 | Minor | 05_results/*.jsonl _meta; Data Availability | Single-environment results, no CI, no repo/DOI; "Reproducible" in title unearned today |
| AD-11 | Minor | tex \S2; PRIOR_WORK_NOTES.md; ledger C008 | Comparative related-work sentences not individually evidence-linked |
| AD-13 | Minor | tex \S1 | Uncited empirical assertion ("risk is concentrated in this layer") |
