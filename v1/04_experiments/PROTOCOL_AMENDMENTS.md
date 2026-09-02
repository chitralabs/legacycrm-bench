# Protocol Amendments

STUDY_PROTOCOL.md v1.0 frozen 2026-09-01. Any change to the protocol after the first paid
model call must be logged here with date, change, reason, and impact on already-collected data.

## A1 — 2026-09-01 (pre-run; no model data collected yet)

**Change:** Candidate execution must be sandboxed (network-denied, scrubbed environment,
rlimits) and run against sanitized case copies containing only tests + candidate solution
(no reference/, no GROUND_TRUTH.md). RQ2 property tagging changed from name-token heuristics
to an explicitly reviewed, frozen per-test tag map. Model slate must include at least one
model from a vendor other than the one whose assistant helped author the benchmark
(conflict-of-interest mitigation).
**Reason:** Internal security review (SP-01, SP-02), benchmark review (tag-token
misclassification), adversarial review (AD-05 authoring-vendor circularity).
**Impact on collected data:** none — no model runs had been executed.

## A2 — 2026-09-01 (pre-run; no model data collected yet)

**Change:** The protocol's "temperature 0" setting is unachievable on the selected 2026
frontier APIs: the Anthropic Claude 5 family removed the temperature parameter, and OpenAI
reasoning-tier models may reject it. The runner therefore sends no temperature parameter,
records the exact parameters of every call, and treats run-to-run nondeterminism as a
measured quantity via the protocol's existing k=5 repeats (pass^k, all-k-agree).
**Reason:** provider API surface change verified against official pricing/docs 2026-09-01.
**Impact on collected data:** none — no model runs had been executed.

## A3 — 2026-09-01 (pre-run; no model data collected yet)

**Change:** Executable model slate is OpenAI-only (gpt-5.6-sol / -terra / -luna, three tiers),
deviating from §4's two-provider rule, because only an OpenAI API key is available in this
environment. The A1 non-authoring-vendor requirement IS satisfied (no Anthropic model is
evaluated; the authoring assistant's vendor is excluded rather than included). If an Anthropic
key becomes available before analysis freezes, the Anthropic arm (claude-opus-5,
claude-sonnet-5) may be added under the same protocol; otherwise the manuscript discloses the
single-provider scope as a limitation.
**Reason:** credential availability; verified 2026-09-01 (auth check via free models.list).
**Impact on collected data:** none — no model runs had been executed.
