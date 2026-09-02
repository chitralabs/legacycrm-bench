# Editorial Desk Review — IEEE Open Journal of the Computer Society (OJ-CS)

**Manuscript:** LegacyCRM-Bench: A Reproducible Benchmark for Evaluating LLM-Assisted Migration of Enterprise CRM Customizations (draft v0.1, `07_manuscript/LegacyCRM_Bench_OJCS_v1.tex`)
**Review role:** Simulated OJ-CS Editor, desk (administrative + scope) screening
**Review date:** 2026-09-01
**Reviewer basis:** manuscript .tex/.pdf, `00_project_admin/OJCS_CURRENT_REQUIREMENTS.md`, `01_literature/NOVELTY_AUDIT.md`, `04_experiments/EVIDENCE_REQUIRED.md`, `09_peer_review_audit/CLAIM_EVIDENCE_LEDGER.csv`, `02_benchmark_dataset/DATASET_CARD.md`
**Disclosure:** This is an internal pre-submission simulation, not an actual OJ-CS decision.

---

## 1. Scope and significance for OJ-CS

**Scope fit: yes.** OJ-CS publishes "high-impact results in all areas of interest to the IEEE Computer Society" and "all aspects of computing" (OJCS_CURRENT_REQUIREMENTS.md §1). A benchmark for LLM-assisted software migration is squarely within software engineering / AI-for-SE, and the journal's CFP explicitly encourages DataPort-linked reproducibility, which this project's design (deterministic harness, machine-generated tables, claim-evidence ledger) matches unusually well. Scope is not the problem.

**Significance: currently thin.** OJ-CS's bar is "high-impact results." As submitted, the paper's only executed results are instrument-validation results (505/505 reference pass, 0/505 null control, 92.3% mutation kill; Results, .tex lines 289–306, verified in CLAIM_EVIDENCE_LEDGER.csv C003–C005). Those are real, well-evidenced, and methodologically commendable — but they establish that the measuring device works, not that it has measured anything. The stated research questions RQ1–RQ4 (.tex lines 172–185) are all explicitly unanswered; the paper itself concedes it answers only "RQ0." A 36-case pilot (3 per category; Limitations item 2, .tex lines 399–400) with no model results is, for a journal, a promissory note. The impact claim rests entirely on future work the manuscript announces but does not contain.

## 2. Novelty relative to existing benchmarks

Assessed against `01_literature/NOVELTY_AUDIT.md` (38 verified references, prior-work matrix):

- The audit's prohibited claims ("first CRM benchmark," "first enterprise benchmark with access controls," "first execution-based translation evaluation," "first migration benchmark," "first legacy-modernization equivalence testing") are all correctly avoided. The manuscript states outright that it "is therefore not the first CRM benchmark and does not claim to be" (.tex lines 122–123) and repeats the disclaimers in Contributions (.tex lines 168–170). This is disciplined and desk-survivable.
- The defensible gap — behavioral preservation of the *customization layer* (rules, workflows, RBAC, audit, integrations) under migration, with executable security-inclusive oracles — is genuinely not operationalized by the CRMArena line, EnterpriseBench/WorkBench/WorkArena/τ-bench (agents operating a fixed environment), or TransCoder/Pan et al./AlphaTrans/PyMigBench/the IBM COBOL line (code translation equivalence). AlphaTrans is the closest methodological relative and is correctly credited (.tex lines 130–131).
- Two hedging defects: the abstract asserts "none measures whether a migration preserves the behavior of configured enterprise customizations" (.tex lines 44–45) and Section III repeats "no existing benchmark measures..." (.tex line 157). These are universal negatives supported only by a 38-reference audit; they should be qualified ("to our knowledge") — the NOVELTY_AUDIT itself is more careful than the manuscript here.
- One rhetorical overreach: "the property that matters most: behavioral preservation" (.tex lines 73–74) is an unsupported importance ranking; state it as the property this benchmark targets, not the one that objectively matters most.

**Verdict on novelty:** sufficient for peer review *if* the paper were otherwise ready. The contribution is a narrow but real gap, honestly bounded.

## 3. Readiness for peer review — the central question

**The paper has no model-evaluation results, and it is an evaluation benchmark.** This is not a marginal judgment call:

1. The title promises "Evaluating LLM-Assisted Migration"; Section VIII confirms "None of C1–C4 has been executed" (.tex lines 286–287); Section X says "No LLM migration results are reported, because the corresponding experiments have not been run" (.tex lines 302–304). RQ1–RQ4 — the paper's own research questions — are all unanswered.
2. The manuscript itself states: "We consider publishing an evaluation-shaped paper without them inappropriate; this draft ... will not be submitted until the protocol's experiments are executed and reported, or the paper is explicitly reframed" (.tex lines 304–306). The authors have pre-agreed with the desk rejection.
3. The project's own evidence register (`04_experiments/EVIDENCE_REQUIRED.md`, E1–E5 and closing paragraph) says the fallback instrument-only framing "is NOT currently recommended without at least one executed model condition."
4. Would OJ-CS desk-reject? **Almost certainly yes, and independently of the results question:** the manuscript carries a "DRAFT — NOT FOR SUBMISSION" watermark (.tex lines 15–21), a draft annotation with an internal cross-reference inside the title (.tex lines 27–28), and "Author Names Pending" with no ORCIDs (.tex lines 32–35) despite IEEE's ORCID-for-all-authors requirement (OJCS_CURRENT_REQUIREMENTS.md §11). It is administratively unsubmittable before any scientific judgment is reached. On the science: a paper whose title, abstract, and RQs frame it as an evaluation benchmark, but whose Results section contains only self-validation of the instrument, would be returned by any competent EiC as premature — most likely "reject / resubmit when experiments are complete" rather than sent to reviewers whose first comment would be identical.
5. A secondary readiness defect the desk would catch: the abstract claims the benchmark and evidence "are released for independent reproduction" (.tex line 54) and the Introduction claims "every reported number is reproducible from the released artifact" (.tex line 100), but Section XVII and Data Availability admit "Repository/DOI placeholder: public hosting and archival deposit are pending" (.tex lines 393–394, 419–420). As written, the release claim is not yet true. Say "will be released" or complete the release first.

**Minimum evidence that would change the decision:**
- Execute at least condition C1 (zero-shot) — preferably C1–C3 — of the frozen protocol on two or more named, exact-identifier models, with k=5 runs (E1, E3 in EVIDENCE_REQUIRED.md), reported with the promised statistics (Wilson CIs, paired bootstrap, McNemar/Holm; E5) and the frozen test→property-class tag map (E6).
- Triage the 28 surviving mutants (E7) so the instrument-validity story is closed, not deferred.
- Complete the administrative blockers: real author list with ORCIDs (E8), official OJ-CS template (E9), live repository + archival DOI so the reproducibility claims are true at submission, and removal of watermark/draft annotations.
- Alternative path, explicitly second-best: reframe honestly as a benchmark-and-instrument resource paper *after* a pre-submission inquiry to the EiC confirming OJ-CS will review that framing (EVIDENCE_REQUIRED.md advises against this without at least one executed model condition, and I concur — even resource papers at strong venues now typically include baseline model results).

## 4. Promotional or unsupported claims

Hunted section by section. Findings:

- **Unsupported (fix required):** "are released for independent reproduction" / "released artifact" (.tex lines 54, 100) vs. pending repository (lines 393–394, 419–420). See §3.5 above.
- **Over-strong universal negatives:** "none measures" (line 44–45), "no existing benchmark measures" (line 157) — hedge to "to our knowledge."
- **Rhetorical overreach:** "the property that matters most" (lines 73–74).
- Otherwise the manuscript is notably non-promotional: no market-size figures (line 66 comment confirms this was checked), no "first-X" claims, no performance claims, limitations are candid and specific (lines 396–406), and every quantitative claim traces to the ledger (CLAIM_EVIDENCE_LEDGER.csv C001–C014, all VERIFIED 2026-09-01). Spot-checks of C001–C005 and C012 against `07_manuscript/generated/numbers.tex` and `generated/T1/T2` confirm the manuscript numbers match the generated macros exactly. This integrity infrastructure is the strongest part of the submission package.

## 5. Desk decision

**DESK REJECT (return without review), with encouragement to resubmit.**

Reasons, in order:
1. Administratively incomplete: DRAFT watermark, draft-note in title, placeholder authors, no ORCIDs, no official template, no live artifact URL (.tex lines 15–35, 393–394; EVIDENCE_REQUIRED.md E8–E9).
2. Scientifically premature: an evaluation-benchmark paper with zero model evaluations; RQ1–RQ4 unanswered; only instrument validation (RQ0) executed. The authors' own text agrees (.tex lines 304–306).
3. The abstract's release claim is not currently true.

What is *not* wrong: scope fit, novelty framing, honesty of the limitations, and the evidence discipline of the executed results. If E1–E9 are completed, this becomes a credible OJ-CS submission; nothing in the underlying instrument work would need to be redone.

*Issues are registered with IDs ED-001 … ED-008 in `09_peer_review_audit/issues_editorial.csv`.*
