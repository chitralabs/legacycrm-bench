# Cycle-2 Editorial + Presentation Review — LegacyCRM-Bench (IEEE OJ-CS)

**Manuscript:** `07_manuscript/LegacyCRM_Bench_OJCS_v1.tex` / `.pdf` (DRAFT v0.3, 2026-09-02; 8 pages; identical copies verified in `10_submission_package/`)
**Review role:** Simulated OJ-CS editor (desk screening update) + IEEE presentation reviewer, cycle 2
**Review date:** 2026-09-02
**Basis:** full .tex read; compiled PDF inspected page by page (8/8); `generated/numbers.tex`, `generated/T1–T3` fragments; cross-checked against `06_figures_tables/M1–M5, run_disposition.csv, T1`, `05_results/model_runs/`, `09_peer_review_audit/ISSUE_REGISTER.csv` + `CLAIM_EVIDENCE_LEDGER.csv`, and the cycle-1 `EDITORIAL_DESK_REVIEW.md`
**Disclosure:** internal pre-submission simulation, not an actual OJ-CS decision.
**Issues registered:** `issues_cycle2_ed.csv` (E2-01 … E2-29).

---

## 1. Desk-review update (the cycle-1 verdict, revisited)

Cycle 1 desk-rejected on two independent pillars: (a) administratively unsubmittable, (b) scientifically premature (evaluation-shaped paper with zero model results).

**Pillar (b) is now cleared.** The manuscript reports a fully executed frozen protocol: instrument validation closed (521/521 reference, 0/521 null, mutation triage loop to 97.0% kill with all survivors classified), an executed deterministic C5 transpiler control (11/36 saturable — exactly the LLM-necessity control cycle 1's adversarial review demanded, AD-02), and 1,980 sandboxed generations across three OpenAI tiers × C1–C4 with k=5, zero infrastructure errors, $33.59 spend under a $150 cap. RQ0, RQ1, RQ3 (directional, honestly flagged underpowered), and RQ4 are answered from executed data; every headline number I spot-checked traces to the machine-generated CSVs (M4 pass^5 values, M5 costs — including the $0.05/$1.19 per-pass figures = cost_usd/5 — the 3–8% C4 overhead, T1 total 521, 11×180=1,980 disposition rows). The claim–evidence ledger has been extended with verified rows C022–C030 dated 2026-09-02. This is no longer a promissory note.

**Pillar (a) still stands.** The manuscript remains administratively unsubmittable, deliberately: DRAFT watermark and draft note inside `\title`, `Author Names Pending` with no ORCIDs, IEEEtran stand-in instead of the mandatory IEEE Open Journals template, and repository/DOI placeholders in Data Availability and Reproducibility. Unverified journal facts (B5) and the independent ground-truth re-derivation (B7) also remain open per `SUBMISSION_BLOCKERS.md`.

**Would I now send it to review if the administrative items were fixed? Yes — after four quick pre-review fixes:**
1. RQ2 is promised but never quantitatively delivered (E2-02): the Setup metrics list pledges "property-class pass rates from a manually reviewed, frozen per-test tag map," and `M3_property_class.csv` exists, but no property-class number or table appears anywhere in the paper; the Results header's "(RQ1–RQ4; Table III)" overstates. One short table or sentence range fixes it.
2. An internal contradiction: Threats says "no confidence interval is attached to the kill rate" while Results reports Wilson 95% CI [94.7, 98.3] on that exact rate (E2-03).
3. A stale results-pending sentence survives in Practical Implications: "claims about tool or model effectiveness await the planned evaluation" (E2-04).
4. Figure 1 is never cited in the text (E2-05).

**Honest remaining scientific soft spots** (disclosed in the manuscript, hence reviewable weaknesses rather than desk-stoppers, but the cover letter should not oversell):
- **Single-vendor slate.** OpenAI-only (logged amendment, credential-forced). The paper's own protocol demanded ≥2 providers; the amendment trades cross-vendor breadth for removal of authoring-vendor circularity and says so. Reviewers will still ask for a second vendor.
- **Near-ceiling scores.** 34–36/36 cases everywhere; the discriminative payload is reliability (pass^5), failure-locus analysis, and the C2 access-narrowing regression. The paper frames this honestly as a calibration result, and the C5 control (a third of cases saturable with no LLM) sharpens rather than undermines that framing — but "benchmark discriminates on three axes" is doing a lot of work over 31 failing generations out of 1,620.
- **Pilot scale / underpowered contrasts.** All condition contrasts are bootstrap-interval-only and flagged underpowered per the pre-committed rule; category rows are descriptive (n=3). Correctly handled, but the empirical contribution is thinner than the instrument contribution.
- **Single environment; independent re-derivation pending.** Both disclosed; B4/B7 gates.

**Updated desk verdict: administratively RETURN (unchanged, deliberate); scientifically NOW REVIEWABLE — would send to reviewers once B2/B3/B4 items and E2-02..05 are fixed.** Nothing in the executed work would need to be redone.

---

## 2. Narrative coherence (task 1)

- **Abstract ↔ Results: consistent.** Every abstract claim (36/521, validation triad, 97.0% kill, 11-case transpiler, 1,980 generations, three models × four conditions, near-ceiling, reliability separation, failure concentration, C2 access-narrowing regression, repair fixes all failures) has a matching executed-results statement and CSV backing. Two nits: the abstract lists three failure loci where Results names four (foreign-key schema reconstruction is dropped; E2-25), and "three commercial models under four … conditions" quietly includes luna, which ran only C1–C3 (E2-26).
- **Introduction/Gap/RQs: updated.** The intro's final paragraph now announces "a complete execution of the frozen evaluation protocol"; the RQ section correctly routes RQ0 first. Residual defects: the Contributions list (Sec. III) still enumerates only the four instrument contributions and omits the executed evaluation/calibration finding — the paper now undersells itself there — and "Sec. X answers RQ1–RQ4" is imprecise (RQ3 is answered in Sec. XI) (E2-14).
- **Results-pending residue:** exactly two spots read as if results were still pending — the Practical Implications sentence (E2-04, Major) and Limitations (6) "The repair-loop condition, when run, depends…" (E2-13, should be "as run").
- **Discussion/Conclusion: neither overreach nor undersell.** "Nearly solved … at the case level," scoped to "this pilot's customizations" and 2026 frontier models; the double-edged conclusion and the "withhold specification completeness" future direction follow from the data. The C5 result is properly used to bound LLM-attributable signal in both places.
- **C5 placement: good.** Defined with the conditions in Setup, reported in Results between instrument validation and model evaluation — the right order (it bounds what the model numbers can mean before they appear). One nit: the Results opener says results "come in two layers" (RQ0 / RQ1–RQ4) and doesn't say which layer C5 belongs to (E2-27).
- **pass^5 tier-ordering claim needs scoping (E2-06, Major):** the quoted ranges (luna 0.889–0.917, terra 0.917–0.972, sol 0.972–1.000) are computed over C1–C3 only, silently excluding C4 where terra hits 1.000 (M4_reliability.csv) — inside sol's range. Also terra=luna=0.917 in C3, so "orders the tiers cleanly" holds per-condition-with-ties, not by disjoint ranges. Say "across the single-shot conditions C1–C3" and soften "cleanly." (Ledger C024 has the same unscoped phrasing.)

## 3. Presentation details (task 3)

**Verified clean:**
- **Abstract: 195 words** (counted from source with macros expanded: 36, 521, 97.0%, 1,980) — under the 250 cap. `FINAL_SUBMISSION_CHECKLIST.md`'s "currently 195" matches.
- **Keywords: 5** (`Benchmarking, software migration, legacy modernization, large language models, access control`) — within the 3–5 guidance, capitalization consistent.
- **Page count: 8 of 12** (pdfinfo; letter; compiled 2026-09-02) — comfortable margin for the template port.
- **Cross-references:** no undefined refs (`??`) in the PDF; all `\ref`s resolve; Tables I–III each cited; no orphaned `\ref`s. Cited section numbers render correctly (Sec. X = Results, etc.).
- **Numbers audit:** Table III body matches M1/M4/M5 exactly; T1/T2 internally consistent (521 total; category sums check); 3–8% C4 overhead and $0.05–$1.19/9–21 s ranges reproduce from M5.
- Cycle-1 presentation fixes held: F1 regenerated un-clipped as `figure*` at `\textwidth` with a self-contained `figures/` path; T1 now has the `\midrule` before Total; DSL/AST expanded; abstract abbreviation-free; refs show "et al." for truncated author lists.

**Defects found:**
- **Figure 1 never cited in text** (label `fig:val`, lines 374–381) — IEEE requires every figure referenced; currently orphaned (E2-05, Major).
- **Table III units/semantics (E2-10):** the `$` column is the **five-run cell total** (M5 `cost_usd`), but the caption says only "total metered cost" and the prose quotes per-pass costs (= column/5); a reader cannot reconcile 4.53 with "$1.19 per pass" without guessing. Say "5-run total" in the caption or add a per-pass column; bare `\$`/`s` headers should read e.g. `Cost (\$)` / `Lat.\ (s)`.
- **Table III grouping (E2-11):** model label only on the first row of each block, no `\midrule` (or `\multirow`) separating the three model blocks; and luna's C4 row is silently absent while the caption promises "per condition (five runs per cell)" — add a `—` row or a caption note ("C4 executed on the frontier and mid tiers only").
- **Notation inconsistencies (E2-12):** table header `p^5` vs text `pass^5`; `pass\textasciicircum{}5` typeset in text mode rather than math (`$\mathrm{pass}^5$`); thousands separators inconsistent — `1980` (macro, no separator) vs `1{,}620`/`1{,}700`.
- **Acronym discipline in the new text (E2-16):** `CI` is used in both new table captions and the kill-rate sentence but "confidence interval (CI)" is never defined; `RQ` likewise never expanded. (AST, DSL, RBAC are properly expanded — cycle-1 fix held.)
- **Macro-discipline drift (E2-15):** the file header claims "All quantitative values are injected from generated/numbers.tex … never hand-edited," but the new Results/Ablation/Failure prose hard-codes many executed numbers (335/363, 92.3%, 28/9/2/17, 11 of 36, 34–36, the pass^5 ranges, $0.05/$1.19, 9–21 s, 25 decisions, 3–8%). All verified correct today — but they are exactly the drift risk the macro rule exists to prevent (same class as cycle-1 PR-015).
- **Bibliography (E2-24):** ref [3] renders "eMNLP 2025" — IEEEtran.bst lowercases the first letter of `note`; protect as `{EMNLP} 2025` in `make_bib.py`/`refs.bib`.
- **IEEE style of the new prose (E2-27):** the reliability sentence is dash-spliced into a run-on ("…orders the tiers cleanly --- luna … sol 0.972–1.000 --- run-to-run nondeterminism, not capability on a single attempt, is where current models differ"); split it. Nineteen numbered sections remain (PR-014 was ACCEPTED pending template port; with results in hand, XIII/XIV/XII invite consolidation).

## 4. Supporting-document consistency (task 4) — stale docs

The ledger and `04_experiments/EVIDENCE_REQUIRED.md` were updated (banner: E1–E7 satisfied, 2026-09-02). Everything else that describes results-state was left at the 2026-09-01 "no results exist" snapshot. **Stale documents found (13):**

| # | File | Stale content |
|---|---|---|
| 1 | `10_submission_package/SUBMISSION_READINESS_REPORT.md` | B1 "No LLM evaluation results (RQ1–RQ4 unanswered) … Remaining: API keys, then execute P1–P3"; Honesty note "Results section reports **instrument validation only**"; "7 pp" (now 8) (E2-08) |
| 2 | `10_submission_package/SUBMISSION_BLOCKERS.md` | B1 "No LLM evaluation results; RQ1–RQ4 unanswered … WAITING ON: API keys"; header "Status: 2026-09-01 (post review-cycle 1)" (E2-08) |
| 3 | `02_benchmark_dataset/DATASET_CARD.md` | Header "Status: pilot instrument; **no LLM evaluation results exist yet**"; validation bullet omits the executed C5 + model evaluation entirely (E2-09) |
| 4 | `08_supplementary_material/REPRODUCTION_GUIDE.md` | "Model-evaluation runs (conditions C1–C4) are NOT included because they have not been executed"; steps end at `aggregate.py`/`measure_inputs.py` — no coverage of `model_analysis.py`, `make_tex_tables.py`, `make_figures.py`, C5, or verifying `model_runs/` against SHA256SUMS. This contradicts the manuscript's Sec. XVII claim that every table is script-reproducible via the guide (E2-07) |
| 5 | `05_results/README.md` | "model_runs/ **(absent)** … absent until authorized runs execute" — the directory exists with P1/P2/P3 JSONL; table also missing rows for `c5_transpiler_baseline.jsonl`, `sandbox_probe_ok.json`, `test_tags.csv` (E2-17) |
| 6 | `10_submission_package/DATA_CODE_AVAILABILITY.md` | "Model-evaluation raw outputs (conditions C1–C4) **do not exist yet**" (E2-18) |
| 7 | `10_submission_package/AI_USE_DISCLOSURE.md` | Component table row "Experimental model results | **NONE EXIST** — nothing AI-fabricated" (E2-19) |
| 8 | `10_submission_package/FINAL_SUBMISSION_CHECKLIST.md` | Evidence boxes now satisfied (B1 runs, sandbox, redaction, tag map, regenerated Results/abstract) remain unchecked with no execution note (E2-20) |
| 9 | `10_submission_package/COVER_LETTER_DRAFT.md` | Results paragraph still the "[PLACEHOLDER — … once model-evaluation experiments have been executed]" — the gating condition is now met; paragraph is writable (E2-20) |
| 10 | `04_experiments/EXPERIMENT_PLAN.md` | Status narrative ends at the mid-P2 credit-exhaustion halt ("resuming requires an account credit top-up"); completion of P2/P3 and final $33.59 outcome never recorded (E2-21) |
| 11 | `09_peer_review_audit/ISSUE_REGISTER.csv` | Rows ED-001, BM-01, AD-01, AD-03 still OPEN-BLOCKER with "no runs executed / neither done" resolutions, though the runs exist (AD-02 was updated; these were not) (E2-22) |
| 12 | `09_peer_review_audit/CLAIM_EVIDENCE_LEDGER.csv` (+ identical copy in `10_submission_package/`) | C010 "No LLM evaluation experiments have been executed … VERIFIED" now contradicts C022–C030; C002's evidence pointer "(acceptance_tests=505)" contradicts the current T1 TOTAL row (521) (E2-23) |
| 13 | `06_figures_tables/README.md` (and `make_tex_tables.py` docstring) | Attributes all CSVs to `aggregate.py`; M1–M5 + `run_disposition.csv` come from `model_analysis.py`; the docstring still claims it writes `T3_mutation.tex` (actual: `T3_model_results.tex` from the M tables) (E2-28) |

Borderline (not counted stale): root `README.md` — its status line correctly delegates to the readiness report (which is stale), and its reproduction workflow omits the model-analysis steps; noted as Editorial E2-29. `EVIDENCE_REQUIRED.md`, `PROTOCOL_AMENDMENTS.md` (A1–A3), `RUN_AUTHORIZATION.md`, `DECISIONS_LOG.md` (dated log entries), `STUDY_PROTOCOL.md` (frozen) are consistent with the new state.

## 5. Issue summary

29 issues registered in `issues_cycle2_ed.csv`: **1 Critical** (carried-forward administrative unsubmittability), **8 Major** (RQ2 gap; kill-rate-CI contradiction; stale results-pending sentence; uncited Figure 1; unscoped pass^5 claim; reproduction-guide gap; readiness/blockers docs; dataset card), **14 Minor**, **6 Editorial**. All OPEN, resolutions empty, for disposition by the project.
