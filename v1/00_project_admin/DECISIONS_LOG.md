# Project Decisions Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-09-01 | Legacy system is fully synthetic ("Meridian CRM 4.2") with a frozen written semantics spec | Integrity rule 12/13: no proprietary artifacts; enables contamination-free tasks and hand-derivable ground truth |
| 2026-09-01 | Ground truth = documented semantics + executable pytest oracles; every expected value carries a written derivation | Integrity rule: no LLM-as-judge; auditability |
| 2026-09-01 | Pilot scale 36 cases (12 categories × 3 difficulties) | Feasible to author+verify rigorously now; scale-up listed as blocker/future work rather than rushing weak cases |
| 2026-09-01 | Cases authored with generative-AI assistance under human-directed process, disclosed in AI-use disclosure and dataset card | Integrity rules 9–10; honesty about process |
| 2026-09-01 | No LLM evaluation runs executed pre-authorization; manuscript cannot present model results | Integrity rules 5 & 16: paid API calls require cost projection + explicit authorization |
| 2026-09-01 | Instrument-validation experiments run offline instead: reference validation, null baseline, AST mutation analysis | Real executable evidence of oracle validity at zero API cost |
| 2026-09-01 | Reference solutions will be publicly released (reproducibility > held-out purity), disclosed as contamination limitation | STUDY_PROTOCOL.md §7 |
| 2026-09-01 | Target OJ-CS constraints from audit: 12-page limit, ≤250-word abstract (IEEE standard), IEEE Open Journals template, IEEE Author Portal | 00_project_admin/OJCS_CURRENT_REQUIREMENTS.md (with flagged unverified items) |
| 2026-09-01 | Manuscript drafted in LaTeX targeting IEEEtran-style OJ template; final compile against official template is a submission blocker (no local LaTeX install; template download must be verified by authors) | Template-compliance rule; no fabricated formatting claims |
