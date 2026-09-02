# LegacyCRM-Bench Study Protocol (v1.0, frozen before any model run)

Written: 2026-09-01. Status: **pre-registration-style protocol; no LLM evaluation runs have been
executed.** This protocol is frozen before the first paid API call; any later amendment must be
dated and logged in `PROTOCOL_AMENDMENTS.md`.

## 1. Research questions

- **RQ1 (Fidelity):** To what extent do LLM-assisted migrations of legacy CRM customizations
  preserve documented behavior, measured by acceptance-test pass rate and case-level
  all-tests-pass rate?
- **RQ2 (Property classes):** Which preservation properties fail most often — functional logic,
  ordering/rounding conventions, security semantics (RBAC scope, deny-by-default), privacy
  exclusions, audit fidelity, or structural completeness (hallucinated/omitted elements)?
- **RQ3 (Condition effect):** Do structured prompting and retrieval of the legacy semantics
  specification improve preservation over zero-shot generation, at what token/dollar cost?
- **RQ4 (Reliability):** How consistent are results across k independent runs (run-to-run
  consistency; pass^k in the sense of tau-bench)?

## 2. Units, sampling, and power

- Unit of analysis: benchmark case (N=36 pilot; 12 categories × 3 difficulties).
- Primary outcome per case and run: all-acceptance-tests-pass (binary). Case-level all-pass is
  primary precisely because per-test counts are not comparable across cases (test granularity
  varies); secondary outcomes: per-test pass proportion (reported with case-level cluster
  bootstrap only, never treating tests as independent), per-property-class pass, tokens,
  latency, cost.
- **Unit-of-analysis rule (frozen).** For Wilson CIs and McNemar tests, the k=5 runs of a cell
  are collapsed to one case-level outcome by majority vote; run-to-run variability is reported
  separately via pass^k and an all-k-agree rate. No statistic mixes runs and cases as if
  independent.
- k=5 independent runs per (model, condition, case) at temperature 0. Seeds are recorded only
  where a provider defines them as meaningful; at temperature 0 they are not relied upon, and
  provider-side nondeterminism is *measured* by the k=5 repeats rather than assumed absent.
  Temperature 0.7 secondary only if budget allows.
- Power note (honest): with N=36 cases, paired comparisons between conditions have limited power;
  we will report exact Wilson 95% CIs for proportions and paired bootstrap (10,000 resamples,
  case-level resampling) CIs for condition differences; McNemar's exact test for paired binary
  outcomes; Holm–Bonferroni across the family of condition pairs per model, and across
  property-class contrasts if any RQ2 contrast is tested rather than described. Detectable
  effect: with 36 paired cases only large condition effects (roughly ≥20 percentage points of
  net discordance) are detectable at conventional power; smaller deltas will be reported with
  CIs and explicitly flagged as underpowered rather than tested to a verdict. We will not claim
  significance for effects the design cannot support; category-level results (n=3 each) are
  reported descriptively only, without tests.

## 3. Conditions (each must be actually executed to be reported)

C0 Null baseline (executed 2026-09-01: empty solution; discriminative-power control).
C1 Zero-shot: single prompt with the case's legacy artifacts + target_spec.md.
C2 Structured prompting: C1 + explicit convention checklist (sentinels, soft delete, ordering,
   collect-all, deny-by-default) + required output file manifest.
C3 Spec-RAG: C2 + retrieved SYSTEM_OVERVIEW.md sections selected by keyword match (deterministic
   retriever, no embedding API; retrieval log saved per call).
C4 Test-feedback repair loop (agentic): C2 + up to 2 repair iterations driven by harness
   failures (patch-only; tests never shown to the model — only failing test names and assertion
   messages with expected values redacted, to avoid oracle leakage; redaction script versioned).
C5 Deterministic transpiler baseline (Amendment A1): a hand-written rule-based transpiler for
   the documented DSLs, run at zero API cost before P1 as an LLM-necessity/headroom control.
All candidate executions for C1–C5 run sandboxed against sanitized case copies (Amendment A1).

## 4. Models

Chosen at authorization time from currently available API models; recorded with exact model ID
string and provider, execution dates, and full request parameters. Planned slate (subject to
authorization and availability check on run day): one frontier-tier, one mid-tier, one small-tier
model from at least two providers, including at least one model from a vendor other than the
one whose assistant helped author the benchmark (Amendment A1, conflict-of-interest
mitigation). No model is named in the manuscript until it has actually been run.

## 5. Metrics (all computed by `03_source_code/` — no hand entry)

Per run: build/parse success; per-test outcomes; case all-pass; per-property-class pass
(property classes read from the manually reviewed, frozen per-test tag map — Amendment A1); security-violation count (failed
security-tagged tests); hallucinated-element count (failed hallucination-tagged tests);
migration completeness (passed completeness-tagged tests); input/output tokens (from API usage
fields); latency (wall clock per request); cost (computed from provider price sheet retrieved on
run day and archived); run-to-run consistency (pass^k, all-k-agree rate).

## 6. Failure handling

API errors: up to 3 retries with exponential backoff; persistent failure recorded as
`infra_error` and excluded from correctness denominators but reported in a run-disposition
table (never silently dropped). If infra_errors exceed 2% of any (model, condition) cell, the
affected case-runs are re-executed once before analysis so that cell denominators do not
drift; both the original and re-run dispositions are reported. Unparseable output (no extractable deliverable files) counts as
build failure (correctness denominator retained). All raw responses stored immutably under
`04_experiments/raw_outputs/<run_id>/` with SHA-256 manifest; nothing is edited post hoc.

## 7. Contamination and leakage controls

- All legacy artifacts and the DSL are novel and authored 2026-09-01; they cannot exist in any
  model's training data. This controls *task* contamination but NOT familiarity with generic
  CRM conventions — stated as a design property, not a guarantee of difficulty.
- Acceptance tests are never included in prompts (C4 sees only redacted failure signals).
- Reference solutions are never included in prompts. Release decision (recorded here):
  reference solutions WILL be released publicly for reproducibility, accepting that
  post-release model training may become contaminated; the dated release note states this, and
  a held-out variant generator is listed as future work. The trade-off is disclosed in the
  paper's limitations.

## 8. What will NOT be claimed

No human-subject evaluation is conducted; no productivity, effort-reduction, or industrial-
deployment claims will be made. Results characterize behavior on a synthetic, documented
legacy system only.
