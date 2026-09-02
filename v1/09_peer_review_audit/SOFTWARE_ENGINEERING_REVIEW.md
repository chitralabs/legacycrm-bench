# Internal Pre-Submission Review 1 — Software Engineering Perspective

**Persona:** Senior software-engineering researcher; background in code translation, test-oracle
design, and industrial replatforming projects.
**Reviewed:** 2026-09-01. Manuscript `07_manuscript/LegacyCRM_Bench_OJCS_v1.tex`; benchmark
`02_benchmark_dataset/`; harness `03_source_code/harness/`; results `05_results/`,
`06_figures_tables/`. Cases read in full: RBC-02, RBC-03, INT-01, INT-03, WFL-03, SCR-02,
CFG-03 (tests), BIZ-02 (target spec), plus all legacy artifacts and the harness source.

**Verdict: Major revision (as an instrument paper); not publishable as an evaluation paper in
its current state.** The engineering is unusually careful for a pilot — validated numbers, a
real null control, real mutation analysis, disciplined provenance. But the equivalence-testing
methodology, the modernization construct, and several harness weaknesses need to be fixed or
honestly re-scoped before external review.

---

## 1. Realism of the migration tasks vs. real replatforming

The single hardest part of real legacy migration is that the semantics are *not* written down:
they are recovered from code archaeology, production incident history, and tribal knowledge.
LegacyCRM-Bench defines this difficulty away by construction: `legacy_system/SYSTEM_OVERVIEW.md`
is a complete, frozen, unambiguous semantics document, and every case's `target_spec.md`
dictates the exact deliverable filenames, function signatures, return shapes, and edge-case
behavior (e.g., `cases/rbac/RBC-03/target_spec.md` specifies the JSON schema down to key names
and `cases/business_rules/BIZ-02/target_spec.md` resolves the actor-vs-owner ambiguity by
fiat). What remains for the solver is closer to *specification-to-code generation under
conventions* than to replatforming. The manuscript's Threats section
(`LegacyCRM_Bench_OJCS_v1.tex`, \S Threats, "External") concedes simplification, but the framing
throughout ("migration of enterprise CRM customizations", title and \S1) is broader than what
the tasks operationalize. **Issue SE-03 (Major).** Required: either add a task tier where the
spec is deliberately incomplete and behavior must be inferred from artifacts + seed data (the
real skill), or narrow the framing in \S1/\S7 to "behavior-preserving reimplementation of
documented legacy customizations."

Also on realism: every case is single-file-scale (deliverables are one or two files,
`case.json` `deliverables` across all 36 cases), there is no cross-case integration migration
except partially BIZ-03, no data migration at volume (716 seed rows,
`legacy_system/seed_data/`, mostly unused by tests per `AUTHORING_GUIDE.md` "Prefer small
hand-crafted fixture rows"), and no cutover/coexistence dimension at all.

## 2. Functional-equivalence approach: per-case pytest oracles vs. differential execution

The benchmark's correctness story is: hand-transcribed expected values in pytest, derived from
prose semantics (`CASE_FORMAT.md` "Every expected value must be derivable by hand"). What it is
*not* is differential testing: **there is no executable implementation of the legacy semantics
anywhere in the artifact.** `03_source_code/` contains no VRL interpreter, no workflow-XML
engine, no CRMScript interpreter. The closest thing is RBC-03's in-test `legacy_can()`
(`cases/rbac/RBC-03/tests/test_acceptance.py`), a hand transcription of \S5 prose used as an
enumeration oracle — good, but unique to that case.

Consequences: (a) oracle coverage is bounded by the authors' imagination of fixtures — WFL
cases test single `fire()` invocations, never event *sequences* through a workflow
(`cases/workflows/WFL-03/tests/test_acceptance.py` is entirely single-step); (b) the
correctness of the hand derivations themselves cannot be machine-checked against executable
legacy behavior, only against the same humans' mutation analysis. The paper cites
AlphaTrans's fragment-wise differential validation as "the closest methodological relative"
(`LegacyCRM_Bench_OJCS_v1.tex`, \S2.2) but does not adopt it. **Issue SE-01 (Major).**
Required: implement reference interpreters for VRL/workflows/CRMScript (they are small; the
DSLs were designed by the same project) and differentially cross-validate every case's
expectations, or explicitly argue in \S Oracles why this was not done and add multi-step
trajectory tests to the workflow cases.

## 3. Test completeness (8–20 tests per case)

Measured: 11–20 test functions per case, 505 total (verified against
`06_figures_tables/T1_benchmark_composition.csv`; per-category sums check out). For the
narrowly-specified deliverables this is defensible density, and the tests I read are
well-targeted (SCR-02's hysteresis boundary tests at 80%/100%, WFL-03's soft-deleted-account
LOOKUP tests, INT-03's absence-of-PII assertions are exactly the right shape).

But the mutation evidence itself says the suites have holes. During this audit cycle a
parallel triage was completed (`09_peer_review_audit/mutant_triage.md`, addressing
`04_experiments/EVIDENCE_REQUIRED.md` E7) and it *confirms* genuine oracle gaps among the 28
survivors (`06_figures_tables/surviving_mutants.csv`): classified TEST_GAPs include `RBC-01`
node 80 (an ADMIN-override mutation survives because **no RBC-01 test ever uses an ADMIN
user**), `RBC-01` node 135 (blank-DEL_FLG DELETE rule untested), `RBC-02` `SVR:'OWN'` (no test
exercises a granting OWN row), `SCH-01` (`owner_id` field never asserted), `ERR-02`
(transient-exhaustion return shape untested), and `INT-02` (blank-CREATE_DT record length
untested). Security-relevant test gaps in the RBAC category are exactly the failure mode the
benchmark exists to catch. **Issue SE-04 (Major).** Required: fix every confirmed TEST_GAP test,
re-run the full validation chain (reference / null / mutation), and report equivalent-vs-gap
counts in \S Failure — the manuscript currently discloses only that survivors "must be
triaged," not the gap findings.

Two systematic completeness gaps: (a) mutation analysis only covers Python deliverables — pure
data deliverables (INT-01's `endpoints.json`, parts of CFG/RIN) get zero mutation validation
(visible in `T3_mutation_sensitivity.csv`: config_modernization has only 12 mutants); consider
data-level mutation (perturb JSON fields, re-run tests). **Issue SE-11 (Minor).** (b) documented
DSL surface that no case exercises: VRL `SUBSTR`, `UPPER`, `CHR` (defined in
`SYSTEM_OVERVIEW.md` \S2/\S4, absent from every test — grep confirms), and workflow escalation
timers are tested only structurally (CFG-03) plus day arithmetic (SCR-03), never as engine
behavior. Dead spec surface weakens the "complete semantics" story. **Issue SE-10 (Minor).**

## 4. Modernization validity: is the target a plausible modern platform?

The "modern platform" is: Python modules with dictated signatures, JSON config documents, and
in one case SQLite DDL (RIN-03). There is no target platform model — no service layer, no ORM,
no declarative rule engine, no workflow product, no IAM system. `policy.json` (RBC-03) is a
reasonable sketch of a modern policy document, and JSON/`enums.json`/`schedule.json` targets
are plausible config modernizations. But calling a bare Python function with a
harness-specified signature "the modern platform's endpoint registry" (INT-01) or "a modern
order service" (BIZ-02) is generous: the target is an artificial Python API optimized for
testability. This choice is defensible (executable oracles need an executable target) but the
paper never defends it, and external validity to migrations targeting actual platforms
(Salesforce Flow/Apex, Dynamics, or even a Django service) is untested and unclaimed but also
undiscussed. **Issue SE-02 (Major).** Required: a subsection in \S Design Goals or \S Threats
explicitly addressing target-construct validity, and ideally one category where the target is a
real framework artifact.

## 5. Code quality — harness and sampled references

References sampled (RBC-02/03, WFL-03, SCR-02, INT-03) are genuinely good: stdlib-only,
deterministic, faithful to sequential legacy evaluation order (SCR-02 preserves the two-IF
sequential semantics of `credit_hold_sweep.crms` and uses `Decimal` to dodge float traps),
defensive about None/missing keys. The harness is small and readable. Defects found:

- `03_source_code/harness/run_all.py`: `run_case()` can raise `subprocess.TimeoutExpired`
  (600 s timeout in `run_case.py`) and `run_all.py` has no try/except — one hung case aborts
  the whole batch mid-JSONL. The run-disposition discipline promised for model runs
  (`STUDY_PROTOCOL.md` \S6) is absent from the instrument harness itself. **SE-06 (Minor).**
- `03_source_code/harness/mutation_check.py`: docstring says SVR applies to "small string
  constants used in comparisons," but `find_mutations()` mutates *every* 1–12-char string
  constant anywhere (dict keys, audit codes, comment-prefix constants), inflating the pool with
  likely-equivalent mutants (AUD-01 `SVR:'#'`, BIZ-01 `SVR:': '` in `surviving_mutants.csv`).
  Doc/code mismatch plus noisier kill-rate denominator. **SE-05 (Minor).**
- `mutation_check.py`: kill criterion is `not res["all_passed"]`, which counts pytest
  infrastructure errors and collection failures as kills; and a mutant that fails
  `ast.unparse` is silently skipped (`except Exception: continue`). Neither is logged.
  **SE-08 (Minor).**
- `03_source_code/harness/validate_cases.py`: does not enforce the upper test bound (only
  `num_tests >= 8`), does not check the CASE_FORMAT.md contract items "at least one negative
  expectation per case" or "a security-scan test where security_expectations is non-trivial",
  and never cross-checks `num_tests` against collected counts (recorded in
  `run_case.py` output but asserted nowhere). The `FORBIDDEN` import regex misses `import os`
  + `os.system`, `__import__`, and aliased/dynamic imports. The manuscript (\S Dataset: "A
  structural validator enforces this contract") overstates what is enforced. **SE-07 (Minor).**

## 6. Generalizability

Twelve categories × 3 cases, one synthetic system, one documented dialect per DSL, one target
language. Category-level conclusions are explicitly descriptive (\S Threats) — good. But the
benchmark cannot support claims about vendor-platform migrations, other target stacks, or
scale effects, and \S Practical Implications should say so more plainly than it does. The
useful generalizable artifact is the *method* (preservation oracles + null control + mutation
validation), and the paper would be stronger if \S Discussion said exactly that.

## 7. Maintainability of released artifacts

Strong points: pinned deps (`03_source_code/requirements.txt`), deterministic regeneration
(`generate_seed_data.py`, byte-identical claim verified by ledger C006), machine-generated
tables with no hand entry, a reproduction guide that matches the actual scripts. Weak points:
`__pycache__` directories are committed inside `02_benchmark_dataset/cases/` (including
`cases/rbac/RBC-03/reference/__pycache__/` and `cases/__pycache__/`) and `.venv/` (5,600+
files) sits inside `v1/` — a release-hygiene pass and a manifest/excludes list are needed;
all executed results come from exactly one environment (macOS 15.7.3 arm64, Python 3.14.2,
per `05_results/*.jsonl` `_meta`) with no CI and no second-platform confirmation. **SE-09
(Minor).**

## 8. What is done right (for the record)

- The null baseline is real and total (0/505, `05_results/null_baseline.jsonl`), and tests
  import deliverables inside fixtures so missing files fail rather than error — verified in
  every sampled case.
- Numbers in the manuscript are injected from `generated/numbers.tex` and I could reproduce
  every total from the CSVs (505, 363, 335, 92.3%, 28, 36, 716).
- `case_lib.py` is a clean seam between tests and solutions; `LCB_SOLUTION_DIR` is the right
  design for candidate substitution.
- GROUND_TRUTH derivations are genuinely load-bearing (SCR-01's half-up boundary derivation
  5.005→5.01 explicitly distinguishes half-up from banker's rounding — the right level of
  care).

## Issue summary (this review)

| ID | Severity | Location | Issue |
|---|---|---|---|
| SE-01 | Major | 03_source_code/ (absent interpreters); tex \S Oracles | No differential/executable legacy semantics; oracles are hand-transcribed fixtures only |
| SE-02 | Major | cases/*/target_spec.md; tex \S Design Goals | Target "modern platform" is an artificial Python/JSON API; construct validity undiscussed |
| SE-03 | Major | SYSTEM_OVERVIEW.md; tex \S1, title | Fully documented frozen semantics removes the defining difficulty of real replatforming |
| SE-04 | Major | surviving_mutants.csv; mutant_triage.md; EVIDENCE_REQUIRED.md E7 | Triage confirms real test gaps (RBC-01 x2, RBC-02, SCH-01, ERR-02, INT-02); fixes + revalidation outstanding |
| SE-05 | Minor | harness/mutation_check.py | SVR operator broader than documented; equivalent mutants inflate pool |
| SE-06 | Minor | harness/run_all.py | Unhandled timeout aborts batch; no per-case disposition in instrument runs |
| SE-07 | Minor | harness/validate_cases.py | Contract items (negative test, security test, ≤20, num_tests match) not enforced; weak import regex |
| SE-08 | Minor | harness/mutation_check.py | Infra errors counted as kills; unparse failures silently skipped |
| SE-09 | Minor | cases/**/__pycache__, .venv/, 05_results _meta | Release hygiene; single-environment validation, no CI |
| SE-10 | Minor | SYSTEM_OVERVIEW.md \S2–\S4 vs cases/ | Documented DSL surface (SUBSTR/UPPER/CHR, behavioral timers) never exercised |
| SE-11 | Minor | T3_mutation_sensitivity.csv; INT-01 | Mutation validation cannot cover data-only deliverables; those oracles are unvalidated |
