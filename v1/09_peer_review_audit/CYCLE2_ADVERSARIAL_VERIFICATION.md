# Cycle-2 Adversarial + Statistics Verification (LegacyCRM-Bench, manuscript v0.3)

Reviewer: cycle-2 adversarial/statistics verifier. Date: 2026-09-02.
Method: full independent recomputation from raw JSONLs (`05_results/model_runs/P2_*.jsonl`,
`P3_*.jsonl`, `P1_pilot.jsonl`, plus `c5_transpiler_baseline.jsonl`, `reference_validation.jsonl`,
`null_baseline.jsonl`, `mutation_results.jsonl`) using `.venv/bin/python` and a from-scratch
script (no reuse of `model_analysis.py` logic); `_meta`/`_halt` rows, mock runs, and
`run_id=P1_pilot` excluded exactly as the frozen rule specifies. Compared against
`06_figures_tables/M1/M2/M4/M5`, `07_manuscript/generated/numbers.tex`,
`generated/T3_model_results.tex`, the compiled PDF (Table III extracted via pdftotext), and
`09_peer_review_audit/CLAIM_EVIDENCE_LEDGER.csv` rows C022–C030.

## 1. Verification table

| # | Claim (location) | Recomputed value | Matches? |
|---|---|---|---|
| V01 | Row census: P2 = 3×3×5×36, P3 = 2×1×5×36, no pilot rows in P2 files | P2 1620 rows, P3 360 rows, total 1980; pilot rows only in P1_pilot.jsonl (36) | YES |
| V02 | Zero infrastructure errors (Setup; run_disposition.csv) | 0 rows with `infra_error`; all 11 cells "completed" ×180 | YES |
| V03 | M1 majority-collapsed all-pass, all 11 (model,condition) cells | luna 36/34/36 (C1/C2/C3); sol 36/36/36/36; terra 36/35/35/36 | YES (exact, incl. Wilson lo/hi at 3 dp) |
| V04 | M4 pass^5 and all-5-agree, all 11 cells | luna .917/.889/.917; sol 1.000/.972/1.000/1.000; terra .972/.917/.917/1.000 (agree identical) | YES (exact) |
| V05 | `\PTwoGens` = 1980 | 1620 (P2) + 360 (P3) = 1980 | YES |
| V06 | `\PTwoFails` = 31; "31 of the 1,620 single-shot generations fail" (Results) | 31 rows with all_passed=false, all in P2 (P3 final outcomes: 0 failures) | YES |
| V07 | `\RepairCalls` = 11, `\RepairUnfixed` = 0 | 11 repair entries (sol 1, terra 10); 0 unrepaired; M5 calls 181/190 consistent | YES |
| V08 | `\SpendTotal` = 33.59 vs `04_experiments/spend_ledger.json` | ledger 33.591857; independent sum of every `cost_usd` (P2+P3+pilot) = 33.5919 — exact match. Ledger `calls`=2071 = 2027 metered (1620+371+36) + 44 zero-cost mock calls (8+36 raw_outputs mock files) | YES |
| V09 | (a) RBC-03 fails ≥1 C2 run for all three models | C2 passes: luna 2/5, sol 4/5, terra 2/5 → fails 3/1/3 runs | YES |
| V10 | (a) RBC-03 majority-fails for terra and luna in C2 | terra 2/5, luna 2/5 (majority fail); sol 4/5 (majority pass) | YES |
| V11 | (a) RBC-03 passes all zero-shot (C1) runs | 15/15 C1 runs pass (also 15/15 in C3) | YES |
| V12 | (b) sol's only failure is RBC-03 C2 run 2 | exactly one sol all_passed=false row: C2, RBC-03, run_index 2 (11/12 tests). NB: sol's C4 run 3 of RBC-03 needed 1 repair before passing — consistent with V07 and not a final failure | YES |
| V13 | (c) failure concentration SCR-01/RBC-03/BIZ-03/RIN-03 | SCR-01 10, BIZ-03 7, RBC-03 7, RIN-03 3 = 27/31; remainder: luna WFL-01 ×2, WFL-02 ×1, SCR-02 ×1 | YES, with caveat (see A2-06: "concentrated on four cases" covers 27/31, not all) |
| V14 | (d) C4 fixed every failure ≤2 rounds | 9 initially-failing C4 rows; rounds {1×7, 2×2}; all final all_passed=true; 36/36 majority, pass^5=1.000 both models | YES |
| V15 | (e) cost $0.05–$1.19 per full 36-case pass (cost_usd/5) | min 0.0536 (luna C1), max 1.1913 (sol C3) | YES |
| V16 | (e) latency 9–21 s mean per case | cell means 9.44 (terra C1) … 20.56 (sol C4) | YES |
| V17 | (f) C4 cost overhead 3–8% vs C2 | sol +3.09%, terra +7.94% (row cost_usd includes repair-call costs — verified in runner line 303) | YES |
| V18 | (g) `'10.5'` vs `10.5` crash exists | 10 crash_messages `AssertionError: assert '10.5' == 10.5` (SCR-01, test_no_audit_when_total_numerically_unchanged) — matches SCR-01's 10 failures | YES |
| V19 | (g) KeyError ACCT_TYP exists | 12 test-level crashes `KeyError: 'ACCT_TYP'` across the 3 RIN-03 failing generations (4 tests each — matches "cascading into four referential-integrity test failures") | YES |
| V20 | (g) close-lost no-op exists | luna C3 WFL-01 crashes: `assert 'P' == 'L'`, `assert 'N' == 'L'`, `assert 'Q' == 'L'` on test_close_lost_from_* (state unchanged = no-op) | YES |
| V21 | (g) 25-decision narrowing exists | "Left contains 25 more items" in sol C2 run 2 and all 3 luna C2 RBC-03 failures; terra's 3 show "23 more items". Manuscript wording ("25 … in one frontier-model output" / "in a single output") is accurate. Direction corroborated: in every failing RBC-03 row, test_no_privilege_widening_anywhere and test_policy_grants_no_triple_absent_from_legacy_matrix PASS → all divergences are narrowings | YES |
| V22 | Pilot exclusion implemented and justified | `EXCLUDED_RUN_IDS={"P1_pilot"}` in model_analysis.py with rationale; pilot = terra C1 ×1, 36/36 pass, $0.4735; gating pre-specified (EXPERIMENT_PLAN "P1 gates P2"); exclusion is outcome-neutral (pilot all-pass; keeps every cell k=5) | YES |
| V23 | Table III (generated tex + compiled PDF) vs M1/M4/M5, cell by cell | all 11 rows × 5 numeric columns match (cases, CI, p^5, $, s); PDF text identical to generated tex | YES (one rounding nit, A2-11) |
| V24 | Wilson CIs independently recomputed | 36/36 [0.9036,1.0000], 35/36 [0.8583,0.9951], 34/36 [0.8186,0.9846] — match M1 at 3 dp | YES |
| V25 | M2 deltas / discordants / underpowered flags | all 15 rows reproduce; every b+c < 8 → all flagged underpowered; "every non-zero delta ≤ 0 for C2/C3 vs C1" confirmed (luna −0.056, terra −0.028/−0.028, sol 0) | YES |
| V26 | pass^5 tier ranges quoted in Results (luna .889–.917, terra .917–.972, sol .972–1.000) | match M4 over C1–C3 (terra C4 = 1.000 sits outside the quoted terra range; ranges are single-shot conditions only — see A2-03) | YES (values) |
| V27 | Instrument numbers: 521/521 reference, 0/521 null, 363 mutants / 352 killed / 97.0% / 11 survivors / CI [94.7, 98.3]; initial 335/363 (92.3%), 28 survivors = 9+2+17 | all recomputed from reference_validation.jsonl, null_baseline.jsonl, mutation_results.jsonl, surviving_mutants.csv, mutant_triage.md; 335+17=352 internally consistent; Wilson for 352/363 = [94.66, 98.30] | YES |
| V28 | C5 transpiler "fully solves 11 of 36; remaining 25 not attemptable; three hard-rated" | c5_transpiler_baseline.jsonl: 11 attempted, 11 all-pass (AUD-01, BAT-01, CFG-01, CFG-03, INT-01, VAL-01/02/03, WFL-01/02/03), 25 skipped; hard = VAL-03, WFL-03, CFG-03 | YES |
| V29 | C4 leakage claim ("no expected values reached the model") | all 11 repair feedback strings scanned: only `<redacted>` placeholders, zero surviving digit runs / quoted literals (e.g. "assert <redacted> == <redacted>") | YES |
| V30 | Mock end-to-end control "scores 36/36" | MOCK_full_pipeline.jsonl: 36/36 all-pass | YES |
| V31 | CLAIM_EVIDENCE_LEDGER C022–C030 | all nine rows' quantitative content reproduces exactly (C025 is even more precise than the manuscript); one label typo in C030 ("C5 cost/latency" should read model/M5 cost-latency) | YES (A2-12) |

**Verification score: 31/31 checks match; 0 numeric mismatches.** Every number in the
abstract, Results, Ablation, and Failure sections traces to raw data and reproduces exactly.

## 2. Adversarial findings (text-level; none numeric)

### A2-01 (Major) — Stale pre-results sentence contradicting the executed evaluation
`07_manuscript/LegacyCRM_Bench_OJCS_v1.tex` Sec. Practical Implications (line 477):
"claims about tool or model effectiveness await the planned evaluation." The evaluation was
executed and is the paper's centerpiece (Results, Ablation, Table III). This is a leftover
from the pre-results draft; it flatly contradicts Secs. Results/Ablation/Conclusion and will
make a reviewer distrust the rest of the revision. Replace with a sentence pointing to the
executed findings (e.g., the C2 regression caution and the repair-loop result).

### A2-02 (Major) — Single-vendor scope leaks into general "2026 frontier models" claims
Only the OpenAI gpt-5.6 family (3 tiers) was evaluated (Amendment A3, disclosed). Yet:
Results line 357–359 "for 2026 frontier-tier models, specification-complete migration … is
largely a solved task"; line 362–363 "where current models differ"; Discussion line 460–461
"2026 frontier models migrate this customization layer near-perfectly"; Conclusion line
562–563 "nearly solved for 2026 frontier models". Threats (lines 499–501) itself states the
conclusions "generalize only to that family". Every headline sentence must be scoped ("the
evaluated gpt-5.6 family" / "the frontier tier evaluated here"), not just the threats section.

### A2-03 (Major) — "cleanly separates the model tiers" oversells pass^5 separation
Abstract line 53–54 ("repeated-trial reliability cleanly separates the model tiers") and
Results line 360–361 ("pass\^{}5 orders the tiers cleanly"). Recomputed facts: in C3, luna
and terra tie exactly (0.917 = 0.917); adjacent tier ranges share endpoints (luna max 0.917 =
terra min; terra max 0.972 = sol min); the quoted terra range (0.917–0.972) silently omits
terra C4 = 1.000; no uncertainty is attached to any pass^5 value. Ordering is strict in only
2 of 3 single-shot conditions. Given the saturation narrative, reliability is the paper's
main residual discriminative claim, so the tie must be acknowledged ("orders the tiers, with
a luna–terra tie in C3") and "cleanly" dropped or defended, and the ranges labeled as C1–C3.

### A2-04 (Major) — Abstract's unscoped, unhedged causal "induces" for the C2 regression
Abstract line 56: "a structured checklist prompt induces access-narrowing regressions" —
generic present tense, no vendor scope, no power hedge. What the data support: within the
evaluated family the direction and mechanism are solid (paired design where only the prompt
differs; RBC-03 fails 7/15 C2 runs vs 0/30 in C1+C3; all divergences are narrowings, since
the no-widening oracles pass in every failing row; C4's C2-based prompt reproduces the same
initial failures). But per the paper's own pre-registered rule, every case-level contrast is
underpowered (all M2 discordant counts < 8; every Holm p = 1.0), and the Ablation correctly
reports "directions without significance claims". The abstract must match that discipline
and the A2-02 scoping: e.g., "a structured checklist prompt reproducibly induced
access-narrowing regressions in all three evaluated models (a directional finding below the
pre-registered power threshold)". The directionality itself verifies; the register does not.

### A2-05 (Minor) — "the only reproducible regression" ignores C3 regressions
Ablation lines 417–419: C2/RBC-03 is called "the only reproducible regression". Recomputed:
terra C3 SCR-01 passes only 1/5 runs (vs 3/5 in C1) and is the sole case behind terra C3 =
35/36; luna WFL-01 fails 2/5 and WFL-02 1/5 runs only in C3. The C2/RBC-03 pattern is unique
in being cross-model with a clean zero-shot baseline; say "the only regression reproduced
across all three models" and note the within-model C3 SCR-01/WFL instability.

### A2-06 (Minor) — "concentrated on four cases" leaves 4 of 31 failures unaccounted
Results lines 363–367: 27/31 failures fall on SCR-01/RBC-03/BIZ-03/RIN-03; the other 4 (all
luna: WFL-01 ×2, WFL-02 ×1, SCR-02 ×1) are never mentioned in Results. The claim ledger's
C025 already words this correctly ("plus scattered luna WFL/SCR-02 failures"); the
manuscript should give the exact split ("27 of 31 concentrate on four cases …").

### A2-07 (Minor) — Threats contradicts Results on the kill-rate CI
Threats lines 482–484: "no confidence interval is attached to the kill rate" — but Results
lines 338–339 attach exactly that (Wilson 95% CI [94.7, 98.3], which recomputes correctly).
Stale text from before the CI was added; delete the clause.

### A2-08 (Minor) — Stale conditional "when run" for the executed C4
Limitations item (6), line 549: "The repair-loop condition, when run, depends on a redaction
mechanism…". C4 was run (11 repair calls, leakage scan clean). Drop "when run".

### A2-09 (Minor) — M5 accounting semantics for C4 rows are internally inconsistent
`06_figures_tables/M5_cost_latency.csv` / `model_analysis.py` lines 206–220 +
`run_experiment.py` lines 294–308: for repaired rows, `input_tokens`/`output_tokens`/
`latency_s` record only the final call, while `cost_usd` sums all calls and `calls` counts
repairs; `mean_latency_s` divides last-call latencies by the repair-inflated call count. No
manuscript number becomes wrong (the 9–21 s and cost claims are robust; costs are correctly
summed), but the released M5 token/latency columns undercount C4 cells and the column
semantics should be documented or fixed before artifact release.

### A2-10 (Editorial) — Abstract's model/condition pairing is loose
Abstract lines 52–53: "\PTwoGens{} sandboxed generations then evaluate three commercial
models under four prompting and repair conditions" — C4 ran on only two of the three models
(1980 = 3×3×5×36 + 2×1×5×36). Setup states this; the abstract should hint it ("repair on the
top two tiers") to avoid implying a full 3×4 grid (which would be 2160).

### A2-11 (Editorial) — Pseudo-quotation of the C2 checklist
Ablation line 421: C2's instruction is quoted as ``deny-by-default; never widen''. The actual
prompt (`04_experiments/prompts/C2_structured.md` item 6) reads "deny-by-default; a missing
permission row means no access; do not widen any permission relative to the legacy matrix."
Either quote verbatim or remove the quotation marks.

### A2-12 (Editorial) — Double-rounding in Table III CI upper bound
`generated/T3_model_results.tex` terra C2/C3: upper CI prints 0.99, but the exact Wilson
upper bound is 0.9951, which rounds to 1.00 at 2 dp; the 0.99 arises from re-rounding the
3-dp CSV value (0.995 → float 0.99499… → "0.99"). Format from full precision (the reported
interval is currently narrower than the true one, the wrong direction to err).

### A2-13 (Editorial) — CLAIM_EVIDENCE_LEDGER C030 mislabeled
`09_peer_review_audit/CLAIM_EVIDENCE_LEDGER.csv` C030's claim text begins "C5 cost/latency:"
but describes model (C1–C4) cost/latency from M5; C5 is the zero-API-cost transpiler.
Relabel (e.g., "Model cost/latency (M5)").

## 3. Checks on the specific adversarial mandates

- **C2-security-regression causality/directionality:** direction fully verified from raw
  oracles (narrowing only; no-widening tests pass in every failing row); cross-model
  replication real (3/3 models, 0/30 baseline failures); causal attribution to the prompt is
  identification-sound (paired manipulation) but the abstract's register exceeds the
  pre-registered power discipline and vendor scope → A2-04, A2-02.
- **Stale pre-results text:** two live instances (A2-01, A2-08) plus one internal
  contradiction (A2-07). Author/DOI placeholders are legitimately-open admin blockers.
- **Saturation-narrative fairness:** the paper is commendably explicit that C5 saturates
  11/36 and that scores are near ceiling; the one oversell is the reliability-separation
  claim (A2-03). Cost as a "discrimination axis" (Results, third axis) is vendor pricing,
  not benchmark power — tolerable but weak.
- **Single-vendor discipline:** violated in four sentences (A2-02) despite a correct threats
  paragraph; abstract's "three commercial models" is accurate.
- **Statistics discipline:** intact in the analysis layer — no p-value is used as a verdict
  anywhere; all 15 M2 contrasts flagged underpowered; unit-of-analysis rule followed;
  Wilson/bootstrap/McNemar implementations recompute correctly. The only lapses are
  presentational (A2-03, A2-04).

## 4. Verdict

All 31 recomputation checks match the raw data exactly — zero numeric errors anywhere in the
abstract, Results, Ablation, Failure Analysis, generated macros, Table III (tex and compiled
PDF), or ledger rows C022–C030. The revision's remaining defects are textual: one
contradictory stale sentence (A2-01), unscoped "2026 frontier / current models"
generalizations (A2-02), and two abstract-level overstatements of separation and causality
(A2-03, A2-04). With those four Major items fixed and the Minor/Editorial items swept, the
empirical content of this manuscript is, in this reviewer's judgment, verification-clean.

Issue register: `09_peer_review_audit/issues_cycle2_adv.csv`
(0 Critical / 4 Major / 5 Minor / 4 Editorial).
