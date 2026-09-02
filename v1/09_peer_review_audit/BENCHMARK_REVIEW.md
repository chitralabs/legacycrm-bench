# Internal Pre-Submission Review 1 — Benchmark/ML Reviewer

**Reviewer persona:** benchmark/evaluation reviewer, top ML/SE venue.
**Artifact reviewed:** LegacyCRM-Bench v1 tree (manuscript `07_manuscript/LegacyCRM_Bench_OJCS_v1.tex`,
dataset `02_benchmark_dataset/`, harness `03_source_code/harness/`, results `05_results/`,
protocol `04_experiments/`). Review date: 2026-09-01.
**Verdict: MAJOR REVISION — not submittable in current form.** The benchmark instrument is
genuinely novel in its object of evaluation, unusually well documented, and its validation
evidence is real and independently reproducible (I reran it; see Review 2). But an
evaluation-shaped benchmark paper with zero model results is below the bar at any serious
venue, the mutation evidence is weaker than the headline number suggests, and the RQ2
measurement instrument (property-class tagging) is demonstrably broken as specified. Issues
are tracked in `issues_benchstats.csv` (BM-*).

---

## 1. Novelty vs. CRMArena(-Pro), EnterpriseBench, PyMigBench, AlphaTrans

The delta is real but narrow, and the project knows it. `01_literature/NOVELTY_AUDIT.md` is
one of the most honest novelty audits I have seen: it enumerates five "must NOT claim" items
and the manuscript complies (`LegacyCRM_Bench_OJCS_v1.tex` §II explicitly disclaims
first-CRM-benchmark status, lines 122–123). The defensible distinction — evaluating
*transformation of the customization layer* (rules, workflows, RBAC, audit, integrations)
for behavioral preservation, rather than agent task execution inside a fixed org (CRMArena
line, EnterpriseBench) or function-level translation (TransCoder/Pan et al./AlphaTrans) or
call-site API migration (PyMigBench) — survives scrutiny against the prior-work notes.
AlphaTrans is the closest methodological relative and is correctly positioned as a technique
lacking a standardized benchmark in this domain.

Is the delta *big enough*? Borderline. The gap claim rests on the conjunction "configured
platform behavior + security semantics + open/deterministic release." Each conjunct alone is
covered elsewhere. What makes this publishable, in my view, is the security/audit/privacy
preservation oracles (RBAC widening, append-only audit, opt-out exclusion), which no cited
prior benchmark operationalizes. But that case must be carried by executed model results
showing the benchmark discriminates and surfaces failure modes that function-level
benchmarks miss. Without them the contribution reads as infrastructure. (BM-01.)

## 2. Dataset construction: the synthetic-DSL design

**Strengths.** The contamination-by-construction and licensing arguments are sound: a
fictional DSL, dated authorship, deterministic seed generation (verified byte-identical in
`CLAIM_EVIDENCE_LEDGER.csv` C006), MIT/CC-BY licensing, no proprietary or personal data.
`SYSTEM_OVERVIEW.md` is a genuinely complete semantics document — I was able to hand-verify
VAL-01 and RBC-03 expectations from it alone. The legacy-convention traps (sentinel dates,
blank-means-default, soft delete, lexicographic date comparison, collect-all validation,
first-match transitions, div-by-zero-yields-zero) are well chosen and are exactly the things
real migrations get wrong.

**Weakness 1: realism.** Read three `target_spec.md` files and the illusion of "migration"
thins. Each case delivers one or two small files against an exact interface
(`convert_account(row) -> dict | None`, `can(user, action, object, record) -> bool`) with
the semantics excerpted into the case (`legacy/SEMANTICS_EXCERPT.md`). This is
*specification-following code synthesis with legacy-convention traps*, not migration as
practitioners experience it: no undocumented behavior to discover, no codebase context, no
cross-file refactoring at scale, no ambiguity about what "done" means. That is a defensible
instrument design (it isolates convention-preservation ability), but the manuscript's
framing ("Enterprises modernizing legacy CRM systems...", §I) invites a stronger reading
than the tasks support. §XV Threats partially concedes this ("synthetic and simplified");
the Introduction should concede it too. (BM-06.)

**Weakness 2: self-referential authoring.** The same project — and, per the disclosure in
`DATASET_CARD.md` and the tex Acknowledgments, largely the same LLM (Claude) under human
direction — wrote the semantics document, the tests, the reference solutions, and the
derivations. The mitigations (written derivations, null baseline, structural validator,
mutation analysis, public release) are necessary but not sufficient: none of them can detect
a *correlated* error, where the spec was misread the same way in the test and the reference.
The 100% reference pass rate is exactly what a correlated error would produce. The one
mitigation that would address this — an independent human (not an authoring participant)
re-deriving expectations for a sample of cases from `SYSTEM_OVERVIEW.md` alone and reporting
agreement — has not been done and is not planned in `04_experiments/EVIDENCE_REQUIRED.md`.
The manuscript's Threats section (lines 370–372) names the risk but the mitigation story is
inadequate for a benchmark whose entire value is oracle trustworthiness. (BM-02.)

## 3. Ground-truth reliability

The GROUND_TRUTH.md files I spot-checked are the strongest part of the dataset.
`cases/rbac/RBC-03/GROUND_TRUTH.md` gives a numbered derivation of the legacy oracle
(deny-by-default, ADMIN row-required/scope-ignored, DELETE requires live record) that I
verified line-by-line against `SYSTEM_OVERVIEW.md` §5/§1, plus spot-checks (items 6–10) that
match the test file. `cases/validation_rules/VAL-01/GROUND_TRUTH.md` derives every expected
code list including the subtle cases (sentinel-date disjunct, empty-string coercion,
WARN-only non-blocking, item 12's all-empty record). `cases/legacy_scripts/SCR-02` correctly
derives the hysteresis band boundaries and the primary-key-order audit vs. input-order
return distinction. These are hand-checkable and I found no derivation errors in the three
cases examined.

Is "AI-authored tests validated by execution + written derivations" defensible? Partially.
Execution validates reference-vs-test *consistency*, not correctness; derivations make the
claimed reasoning auditable, which is more than most benchmarks offer. The claim "LLM-derived
expectations are forbidden" (`CASE_FORMAT.md`, test contract) is a process assertion that
cannot be verified from the artifact — an LLM drafted the derivations too. The defensible
formulation is: expectations are *auditable against the frozen spec by any reader*, and the
authors invite that audit. The paper mostly says this (§VII "Authoring process (disclosed)"),
which is good; it should not say more than this. Residual requirement: the independent
re-derivation audit of BM-02, and completion of the surviving-mutant triage (E7 in
`EVIDENCE_REQUIRED.md`, currently not done — `09_peer_review_audit/mutant_triage.md` does not
exist). (BM-11.)

## 4. Metric validity

**All-tests-pass is coarse, and test granularity is wildly uneven.** RBC-03 compresses a
720-tuple decision-equivalence check into *one* test function
(`test_full_decision_equivalence_with_legacy_matrix`), so a candidate failing 1 of 720
tuples and a candidate failing all 720 score identically, and RBC-03's per-test pass rate
moves in increments of 1/12. INT-03 by contrast spreads 14 fine-grained tests over similar
behavioral surface. Per-test pass proportions are therefore not comparable across cases, and
the secondary "per-test pass proportion" metric in `STUDY_PROTOCOL.md` §2 inherits this
distortion. Recommend reporting case-level all-pass as primary (as planned) and, for
diagnostic tests like RBC-03, emitting tuple-level counts as a case-local metric. (BM-09.)

**The property-class tagging plan (RQ2) is broken as specified.** `EXPERIMENT_PLAN.md`
("Preservation-property tagging") assigns classes by name-token matching
(`security`/`privilege`/`optout`/`credential`/`forbidden`; `invented`/`hallucin`/`no_extra`;
`preserved`/`complete`/`all_`). I simulated this map over all 505 collected test names:

- Only 29/505 tests tag as security. The two flagship privacy tests of INT-03,
  `test_opted_out_contact_id_never_in_payload` and
  `test_opted_out_contact_email_and_name_never_in_payload`, do **not** match — the token is
  `optout` but the test names spell `opted_out`. Meanwhile
  `test_blank_optout_flag_means_included` — a *functional inclusion* test — **does** tag as
  security. The tagging inverts the classification inside the very case built to showcase
  privacy preservation.
- `test_pref_ch_phone_preserved` (INT-03, functional field mapping) tags as completeness via
  the `preserved` token.
- RBC-03's `test_no_forbidden_imports_and_no_invented_ecodes` matches two classes; the plan
  has no tie-break rule.
- RBC-03's `test_admin_denied_without_grant` and `test_full_decision_equivalence_...` — the
  core security oracles — tag as functional.

`analysis/tag_tests.py` does not exist yet, and the plan's "manual review of the map" is the
only thing standing between these errors and the RQ2 results. This must be fixed before P1:
either explicit per-test markers (`@pytest.mark.security`) enforced by the validator, or a
hand-audited tag file per test, with the name-token heuristic demoted to a first-pass
generator. (BM-05; cross-ref ST-08.)

**Mutation analysis: headline number overstates oracle strength.** See Review 2 (ST-02) for
the statistics; the benchmark-design points are: (a) the operator mix is dominated by string
mutation — 267/363 mutants (73.5%) are SVR, vs 67 ROR, 20 AOR, 9 CBR (recomputed from
`05_results/mutation_results.jsonl`) — so the 92.3% kill rate mostly measures sensitivity to
string-constant perturbation, the easiest class to kill; (b) mutation covers **only Python
deliverables**: `mutation_check.py:mutants_for_case` globs `reference/*.py`, so CFG-01
(`enums.json`), CFG-03 (`workflows.json`), and INT-01 (`endpoints.json`) received **zero
mutants**, and mixed cases' JSON/SQL deliverables (RBC-03 `policy.json`, BAT-01
`schedule.json`, RIN-03 `modern_schema.sql`) are never mutated. Config-migration
correctness is a headline claim of this benchmark, and its config oracles have no
sensitivity evidence at all. The manuscript (§X "Mutation sensitivity") does not disclose
either fact. (BM-03, BM-04.) Also note untriaged security-relevant survivors: RBC-01
`SVR:'ALL'` and `SVR:'N'`, RBC-02 `SVR:'OWN'`, RBC-03 `CBR:bool`
(`06_figures_tables/surviving_mutants.csv`) — until triaged, a reviewer must assume the RBAC
oracles have gaps.

## 5. Baselines and model selection

None run, by declared integrity rule — and the draft is admirably explicit about it
(watermark, §IX "What does not exist yet"). But the paper cannot be reviewed as an
evaluation instrument without evidence the instrument discriminates *among real systems*,
not just between reference and null. Minimally credible slate for a first submission:

- One frontier proprietary model from **each of two providers** (e.g., a Claude-family and a
  GPT-family frontier model, exact IDs recorded at run time per protocol §4);
- One mid-tier proprietary model (cost/quality point);
- One strong open-weights model (e.g., a current Llama/Qwen-class coder), because open
  models make the benchmark's contamination story testable and results reproducible without
  API access;
- Conditions C1 and C2 at minimum, k=5, per the frozen protocol. C3/C4 can be follow-up.

**Conflict to disclose and mitigate:** the benchmark's artifacts were authored with Claude
(`DATASET_CARD.md`, tex Acknowledgments), and the *only* concrete slate anywhere in the
project is the all-Anthropic illustrative slate in `04_experiments/ESTIMATED_COSTS.md`
(Opus 5 / Sonnet 5 / Haiku 4.5) — which contradicts `STUDY_PROTOCOL.md` §4's own "at least
two providers" requirement. An Anthropic-authored benchmark evaluated only on Anthropic
models would be uninterpretable (authoring-model familiarity cuts in both directions and is
unmeasurable). The two-provider rule must be honored and the authoring-model relationship
disclosed in the paper's evaluation section, not just the Acknowledgments. (BM-07.)

## 6. Contamination

The pre-release position is strong: novel DSL, dated artifacts, no-tests-in-prompts rule,
redacted repair signals (protocol §7). Two residual points are handled honestly but deserve
prominence: (a) the release decision ships tests *and* reference solutions, so every
post-release model is presumptively contaminated; the held-out-variant generator is "future
work" — for a benchmark whose main use begins after release, that is a structural weakness,
not a footnote (Limitations item 5 says it; the Discussion should too). (b)
Generic-convention familiarity: models have seen thousands of YYYYMMDD-sentinel, Y/N-flag,
deny-by-default implementations; the novel-DSL argument controls provenance of the *task
text*, not difficulty. The protocol §7 says exactly this — good. (BM-08.)

## 7. Reproducibility of the pipeline

Verified by execution (details in Review 2): `validate_cases.py` reports 36 cases / 0
errors; a fresh `run_all.py --solution reference` run reproduced all 505/505 per-test
outcomes identically; the aggregation chain (raw JSONL → `aggregate.py` CSVs →
`make_tex_tables.py` macros) is consistent end-to-end, and `CLAIM_EVIDENCE_LEDGER.csv` maps
every quantitative claim to a source file. This is above community standard. Remaining gaps:
pinning covers packages (`03_source_code/requirements.txt`) but not the Python version
(3.14.2 is recorded, not enforced); the repro guide has no expected checksums; the harness
has robustness/safety gaps that will bite when running *model-generated* code (uncaught
timeout, no sandbox — ST-06). Hygiene: `.venv/` and `__pycache__` directories are inside the
release tree (`v1/.venv`, `cases/*/*/tests/__pycache__`, `reference/__pycache__`) and should
be excluded from any public artifact. (BM-12, BM-13.)

## 8. Scale

36 cases / 3 per category is honestly labeled a pilot (G7, Limitations 2), and the *stated*
claims (instrument validity) do not need more. The risk is inferential leakage: Tables I–II
present 12 per-category rows, and readers will rank categories from n=3 descriptive numbers
(e.g., validation_rules 83.3% kill vs referential_integrity 100%). The paper says
"descriptive only" in §XV; the table captions should carry that label too. For any future
model-comparison claims, 36 cases yields wide CIs (a Wilson 95% CI at 50% observed is
roughly ±16 points) — condition deltas will need to be large to be detectable, which the
protocol's power note concedes without quantifying (ST-05). (BM-10.)

## 9. Verdict

**Major revision / not yet submittable**, in agreement with the project's own
`EVIDENCE_REQUIRED.md` gating. Required before submission: (1) execute at least the minimal
model slate above (E1); (2) fix the property-class tagging instrument; (3) either extend
mutation to config deliverables or disclose the coverage boundary and rebalance the operator
mix; (4) commission an independent re-derivation audit for a case sample; (5) complete
surviving-mutant triage; (6) honor the two-provider rule and disclose the authoring-model
conflict. The underlying instrument is good enough to be worth this work.
