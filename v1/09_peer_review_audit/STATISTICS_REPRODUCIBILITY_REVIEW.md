# Internal Pre-Submission Review 2 — Statistics & Reproducibility Reviewer

**Reviewer persona:** statistics and reproducibility reviewer.
**Scope:** `04_experiments/STUDY_PROTOCOL.md` + `EXPERIMENT_PLAN.md` (planned statistics),
`05_results/*.jsonl` + `06_figures_tables/*.csv` + `07_manuscript/generated/numbers.tex`
(executed numbers, which I independently recomputed), `03_source_code/harness/*` (pipeline),
`08_supplementary_material/REPRODUCTION_GUIDE.md` (which I followed, steps 2–3).
Review date: 2026-09-01.
**Verdict: statistics plan is directionally sound but underspecified at the unit-of-analysis
level; the executed instrument-validation numbers fully reproduce — every number I recomputed
matched the manuscript macros exactly.** Issues tracked in `issues_benchstats.csv` (ST-*).

---

## 1. Traceability: independent recomputation (executed)

I recomputed the manuscript's quantitative claims directly from the raw JSONL with Python,
bypassing `aggregate.py`:

| Quantity | Recomputed from raw | Manuscript macro (`generated/numbers.tex`) | Match |
|---|---|---|---|
| Cases in `reference_validation.jsonl` | 36 | `\NumCases{36}` | YES |
| Tests collected (sum `num_tests_collected`) | 505 | `\NumTests{505}` / `\RefTotal{505}` | YES |
| Reference tests passed | 505; `all_passed` true for all 36 | `\RefPassed{505}` | YES |
| Null-baseline tests passed (`null_baseline.jsonl`) | 0 of 505 | `\NullPassed{0}` | YES |
| Mutants (`mutation_results.jsonl` records) | 363 | `\NumMutants{363}` | YES |
| Mutants killed | 335 (92.2865%) | `\MutantsKilled{335}`, `\KillRate{92.3}` | YES (correct rounding) |
| Surviving mutants | 28 | `\SurvivingMutants{28}` | YES (and 28 rows + header in `surviving_mutants.csv`) |

Cross-checks: `case.json` `num_tests` equals collected count for all 36 cases; T1/T2/T3 CSV
totals and the LaTeX table bodies in `07_manuscript/generated/` are consistent with the raw
files; category rows in `T2_groundtruth_validation.csv` and `T3_mutation_sensitivity.csv`
recompute correctly. `CLAIM_EVIDENCE_LEDGER.csv` claims C001–C005 and C012 are confirmed.
**No discrepancies found.**

## 2. Reproduction guide, steps 2–3 (executed)

Step 2 (`.venv/bin/python 03_source_code/harness/validate_cases.py`): output
`validated 36 cases; 0 errors` — matches the guide's expectation and ledger C007.

Step 3 (`run_all.py --solution reference`): I ran it writing to a scratch directory instead
of the guide's in-place path (see discrepancy (a) below). Result: 36/36 cases all-pass,
505/505 tests; per-test `(nodeid, outcome)` sequences are **identical** to the archived
`05_results/reference_validation.jsonl` for every case. Determinism claim confirmed on the
recorded platform (same machine class, Python 3.14.2 venv). Mutation was not rerun (slow),
per instruction; its JSONL was recomputed instead (§1).

Discrepancies/weaknesses in the guide itself (ST-07):
- (a) **Destructive verification.** Steps 3–5 write their output *over the archived raw
  results* (`--out 05_results/reference_validation.jsonl` etc.). A reproducer who gets a
  different result has just destroyed the evidence they needed to diff against. The guide
  should direct output to a fresh directory and ship a comparison script.
- (b) **No expected checksums.** Step 1 says "verify byte-identical output" via `shasum` but
  publishes no reference hashes (the ledger C006 has only a truncated SHA-1). Steps 3–5 give
  qualitative expectations only. Publish SHA-256 of seed CSVs and of a canonicalized
  (timestamp-stripped) form of each JSONL.
- (c) **Python version not enforced.** `requirements.txt` pins packages, but nothing checks
  the interpreter is 3.14.x; the guide merely records it. `python3 -m venv` will silently
  use whatever the reproducer has.
- (d) The `_meta` headers correctly warn that timestamps differ; everything else matched, as
  claimed.

## 3. Sample size and planned inference

The protocol (§2) plans Wilson 95% CIs for proportions, paired case-level bootstrap (10k)
for condition deltas, exact McNemar for paired binaries, Holm–Bonferroni across condition
pairs per model, and refuses per-category tests (n=3). All appropriate choices as far as
they go. Gaps:

- **Unit of analysis is underspecified once k=5 runs exist (ST-01, Major).** The primary
  outcome is case-level all-pass, but each (model, condition, case) cell has 5 binary
  outcomes. Which quantity enters the Wilson CI over 36 cases — run 1, majority-of-5,
  any-of-5, or the mean of per-run proportions? Which enters McNemar's paired table? McNemar
  requires one binary per case per condition; with 5 correlated replicates per cell the
  protocol must either pre-specify the collapse rule (and justify it) or use a method that
  models replicates. This is exactly the kind of degree of freedom a pre-registration-style
  protocol exists to remove, and it is open.
- **Clustering of tests within cases (ST-01).** The secondary "per-test pass proportion"
  aggregates 505 tests that are clustered in 36 cases with strongly correlated outcomes
  (all-or-nothing failure modes; a missing deliverable fails a whole case). A Wilson CI on
  505 Bernoulli trials is invalid here — the effective sample size is nearer 36 than 505.
  Any test-level CI must be cluster-aware (bootstrap over cases, which the plan already has
  for deltas — extend it to levels). Test granularity is also grossly uneven across cases
  (RBC-03 packs a 720-tuple equivalence check into one test; see BM-09), so per-test
  proportions are not comparable across cases even before clustering.
- **Property classes multiply the families (ST-08, Editorial).** RQ2 compares failure rates
  across ≥6 property classes; the multiplicity plan only covers condition pairs per model.
  State whether property-class contrasts are descriptive or tested, and if tested, what the
  family is. (Note RQ2's measurement instrument is itself broken as specified — the
  name-token tag map misclassifies INT-03's privacy tests; detailed under BM-05.)
- **Power is acknowledged but never quantified (ST-06, Minor).** "Limited power" should be
  made concrete: e.g., with N=36 paired cases, McNemar's exact test at α=.05 needs roughly
  ≥8–9 discordant pairs in one direction to reach significance; a Wilson 95% CI at 18/36
  observed spans ≈±16 points. One sentence of minimum-detectable-effect arithmetic would let
  readers judge which RQ3 deltas the design can resolve.

## 4. Repeated runs, temperature 0, determinism (ST-04)

k=5 at temperature 0 is defensible *because* major providers are nondeterministic at temp 0
(batching/MoE/floating-point effects), but the protocol never says so — and its own wording
is internally muddled: "k=5 independent runs ... with distinct seeds where the API supports
them; temperature 0" (§2). At temp 0, seeds are a no-op where sampling is disabled and a red
herring where it is not. The protocol should (a) state explicitly that temp-0 outputs may
differ and that this is the phenomenon pass^k measures; (b) record a response-content hash
per run and report the duplicate-rate, since if all 5 responses are byte-identical, pass^k
degenerates and the 4 extra runs are wasted budget — a pre-specified early-stop rule
("if runs 1–2 identical, ...") would be better than discovering this after spend; (c) define
pass^k's estimator given k=5 (tau-bench's combinatorial estimator or the plug-in — name it).

## 5. Missing data / failed runs (ST-05)

The rules in protocol §6 (3 retries, `infra_error` excluded from correctness denominators
but reported in a run-disposition table; unparseable output = build failure retained in the
denominator; immutable raw storage) are better than most published work. Two gaps:
- Denominator instability: excluding infra errors makes each cell's N a random variable; with
  N=36, even 2 exclusions shift a proportion by ~6%. Pre-specify a re-run policy (infra
  errors are re-queued until k valid runs exist or a cap is hit) or a sensitivity analysis
  (report best/worst-case bounds treating infra errors as pass/fail).
- Partial-k cells: pass^k with fewer than k valid runs is undefined in the plan — specify
  (compute at the largest available k' and flag, or exclude cell).
- Timeout of *candidate* code is not classified: is a 600s pytest timeout an infra error or
  a correctness failure? For model-generated code an infinite loop is a model failure, not
  infrastructure; the current harness makes this moot by crashing instead (see §7).

## 6. Mutation analysis statistics (ST-02, Major)

Recomputed facts (`mutation_results.jsonl`, `mutation_check.py`):
- Operator mix: SVR 267 (73.5%), ROR 67, AOR 20, CBR 9. Survivors: 25 of 28 are SVR.
- Per-case mutant counts range 3–12 (cap 12); **three cases received zero mutants** —
  CFG-01, CFG-03, INT-01, whose only deliverables are JSON — because `mutants_for_case`
  mutates only `reference/*.py`. Non-Python deliverables (RBC-03 `policy.json`, BAT-01
  `schedule.json`, RIN-03 `modern_schema.sql`) are never mutated anywhere.
- Overall kill rate 335/363 = 92.29%; Wilson 95% CI **[89.1%, 94.6%]** — not reported in the
  manuscript, which gives the point estimate only.

Critiques:
1. **Selection bias.** The cap-12 "even spread" (`out[int(i*step)]`) samples the mutation-site
   list in AST-walk order without stratifying by operator, so the operator mix simply mirrors
   site prevalence — string constants dominate legacy-convention code, hence 73.5% SVR. SVR
   mutants are the easiest to kill (any exact-match assertion kills them), inflating the
   headline rate relative to a balanced ROR/AOR/CBR mix. Stratify selection per operator, or
   report kill rates per operator (killed/total: SVR 242/267 = 90.6%, ROR 65/67, AOR 20/20,
   CBR 8/9 — the near-perfect logic-operator rates are actually the better news and go
   unreported).
2. **Coverage asymmetry silently absorbed.** T3's per-category rates average over cases with
   3–12 mutants and *exclude* the zero-mutant cases from the analysis without disclosure;
   config_modernization's "12 mutants, 91.7%" row is CFG-02 alone. The manuscript's mutation
   claim should state the boundary: sensitivity evidence exists only for Python deliverables.
3. **No uncertainty, unit issues.** Mutants are clustered within cases (shared tests), so the
   363-Bernoulli Wilson CI above is itself optimistic; a case-level bootstrap would be
   consistent with the rest of the statistical plan. Per-category kill rates on 12–36 mutants
   are presented (T3, Table II) with no CIs — label descriptive.
4. **Survivors unresolved.** 28 survivors await the E7 triage (equivalent vs test gap);
   `09_peer_review_audit/mutant_triage.md` does not exist. Until triaged, the kill rate's
   interpretation (oracle strength vs equivalent-mutant floor) is indeterminate — and several
   survivors sit in security cases (RBC-01 ×2, RBC-02, RBC-03).
5. Minor mechanics: a mutant that fails `ast.unparse` or produces an import-crashing module
   counts as killed via `all_passed=False` (standard but conflates crash-kill with
   assertion-kill; report the split), and mutants skipped by exceptions are silently dropped
   from the denominator (`continue` in `mutation_check.py` main loop).

## 7. Pipeline robustness for the *planned* runs (ST-03, Major)

The executed pipeline is deterministic and clean (PYTHONHASHSEED=0, no network, `-p
no:cacheprovider`, tmp-dir isolation). But it has only ever run trusted code. For
model-generated candidates:
- `run_case.py` passes `timeout=600` to `subprocess.run` and never catches
  `subprocess.TimeoutExpired`; a single hanging candidate raises out of `run_case` and
  **aborts the entire `run_all.py` batch mid-file**, leaving a truncated JSONL. Catch it and
  record a per-case timeout disposition.
- No sandboxing: candidate code executes with full user privileges and live network. The
  static forbidden-import scan in `validate_cases.py` applies only to tests and reference
  solutions, never to candidates; `case.json` `failure_conditions` ("network access") is
  aspirational — nothing detects or prevents it at run time. Before P1, run candidates in a
  network-disabled subprocess/container and record enforcement in the protocol.

## 8. Summary

Everything executed is real, internally consistent, and reproduced exactly in my hands:
**both recomputed quantities (505/505 reference tests; 335/363 = 92.3% mutation kill) match
the manuscript macros, as do all subsidiary numbers I checked.** The statistical *plan*
needs one round of sharpening before any paid run: fix the unit-of-analysis/collapse rules
(ST-01), stratify and CI the mutation evidence (ST-02), harden the harness against untrusted
code (ST-03), and make the reproduction guide non-destructive with published checksums
(ST-07). None of these requires new science; all of them are cheaper to fix now than after
data exist.
