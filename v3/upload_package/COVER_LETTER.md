# Cover Letter (DRAFT — do not send until blockers in SUBMISSION_READINESS_REPORT.md are cleared)

To the Editor-in-Chief, IEEE Open Journal of the Computer Society:

Dear Editor,

We submit "LegacyCRM-Bench: A Reproducible Benchmark for Evaluating LLM-Assisted Migration of
Enterprise CRM Customizations" for consideration as a regular paper.

Enterprises modernizing legacy CRM deployments must migrate not only data but a customization
layer — validation rules, workflow automations, scripts, access-control matrices, integrations,
and audit behavior — and LLM assistance is increasingly proposed for this work. Existing CRM
benchmarks (CRMArena, CRMArena-Pro) evaluate agents operating inside a fixed CRM; existing
translation and migration benchmarks evaluate function- or library-level code. None measures
whether a migration preserves the behavior of configured enterprise customizations, including
security semantics. LegacyCRM-Bench addresses this gap with a fully synthetic, documented
legacy CRM, 36 migration cases across 12 categories, and executable preservation oracles
validated by reference solutions, null-baseline controls, and mutation analysis.

Beyond the instrument itself, the paper reports a fully executed, sandboxed, budget-capped
evaluation: a deterministic transpiler control (which solves 11 of 36 cases, bounding the
share requiring no model) and three OpenAI model tiers under four prompting and repair
conditions (1,980 generations, zero infrastructure errors). The results calibrate the field:
case-level scores are near ceiling under complete specifications, while repeated-trial
reliability separates model tiers, failures concentrate on legacy-convention and
access-control-equivalence oracles, and a structured checklist prompt reproducibly induces
access-narrowing regressions that zero-shot prompting avoids — with a redacted-feedback
repair loop fixing every observed failure.

This manuscript is original, is not under consideration elsewhere, and the author has
approved it. Generative-AI assistance in preparing the manuscript and artifacts is disclosed
in the Acknowledgments per IEEE policy. All artifacts will be publicly available (see Data
Availability). I have no conflicts of interest to declare.

Sincerely,

Chitrapradha Ganesan, Senior Member, IEEE
Post Graduate Program in Artificial Intelligence and Machine Learning
The University of Texas at Austin, Austin, TX 78712, USA
ORCID: 0009-0009-1305-1724 · chitracrmexpert@gmail.com
