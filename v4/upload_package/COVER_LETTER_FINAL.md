# Cover Letter

To the Editor-in-Chief, IEEE Open Journal of the Computer Society:

Dear Editor,

I submit "LegacyCRM-Bench: A Reproducible Benchmark for Evaluating LLM-Assisted Migration
of Enterprise CRM Customizations" for consideration as a regular paper.

Enterprises replatforming legacy CRM deployments must migrate not only data but a
customization layer — validation rules, workflow automations, scripts, access-control
matrices, integrations, and audit behavior — and LLM assistance is increasingly proposed
for this work. Existing CRM benchmarks (CRMArena, CRMArena-Pro) evaluate agents operating
inside a fixed CRM; existing translation and migration benchmarks evaluate function- or
library-level code. To my knowledge, none measures whether a migration preserves the
behavior of configured enterprise customizations, including their security semantics.
LegacyCRM-Bench addresses this gap with a fully synthetic, completely documented legacy
CRM, 36 migration cases across 12 categories, and executable preservation oracles validated
by reference solutions, a null-baseline control, and a mutation audit that strengthened the
test suites before any model was evaluated.

Beyond the instrument, the paper reports a fully executed, sandboxed, budget-capped
evaluation: a deterministic transpiler control (which solves 11 of the 36 cases, bounding
the share requiring no model) and three commercial model tiers under zero-shot, guided
prompting, retrieval, and repair conditions (1,980 protocol generations, zero
infrastructure errors). The results are deliberately calibrational rather than promotional:
case-level scores are near ceiling under complete specifications, while repeated-trial
reliability separates the model tiers, the remaining failures concentrate on
legacy-convention and access-control-equivalence oracles, and a structured checklist prompt
is accompanied by reproducible access-narrowing regressions that zero-shot prompting
avoids. Limitations — the single-vendor model slate, the 36-case pilot scale, and the
synthetic environment's bounded realism — are stated in the manuscript.

The complete artifact is publicly available: the repository at
https://github.com/chitralabs/legacycrm-bench (repository tag v0.1; archival release
v0.1.1) is permanently archived on Zenodo under DOI 10.5281/zenodo.22777518, including all
raw run logs with SHA-256 manifests, and the offline validation pipeline is reproduced
continuously on an independent Linux environment in the repository's integration workflow.

This manuscript is original, is not under consideration elsewhere, and the author has
approved it. Generative-AI assistance in preparing the manuscript and artifacts is
disclosed in the Acknowledgment per IEEE policy. I have no conflicts of interest to
declare. This work received no external funding.

Sincerely,

Chitrapradha Ganesan
Independent Researcher, Dallas, TX, USA
ORCID: 0009-0009-1305-1724 · chitracrmexpert@gmail.com
