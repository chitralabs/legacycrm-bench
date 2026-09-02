# Dry-Run Cost Projection for Planned LLM Experiments

Date: 2026-09-01. **No paid API calls have been made.** This projection must be re-verified
against current provider price pages on the day authorization is granted, and a hard budget cap
must be set before the first call.

## Measured inputs (real, from `05_results/input_size_measurements.csv`)

- One full C1 pass over all 36 cases: **91,850 approx input tokens** (chars÷4 heuristic over
  the exact prompt payloads; replace with the provider's `count_tokens` endpoint at
  authorization for exact figures).
- Reference-solution output size: **16,860 approx tokens** per full pass. Models are typically
  more verbose; output is budgeted at 2× reference size (≈34k tokens/pass) for estimation and
  capped at 4× in the runner.

## Price basis

Anthropic API list prices (from the Claude API reference bundled with the tooling, cached
2026-06-24 — RE-VERIFY at https://claude.com/pricing or the API docs before running):
Claude Opus 5 $5/$25 per MTok (in/out); Claude Sonnet 5 $2/$10; Claude Haiku 4.5 $1/$5.
Batch API runs at 50% of these rates and is acceptable for C1–C3 (no interactivity needed).
Non-Anthropic models: **no verified price is quoted here**; pull the provider's current price
page at authorization time and append it to this file with retrieval date.

## Projection formulas (per full 36-case pass)

cost ≈ (0.0919 × price_in) + (0.034 × price_out), in MTok units.
C2 adds the fixed checklist (~0.4k tokens/case → +14k in/pass); C3 adds retrieved spec
sections (~1.5k tokens/case → +54k in/pass). Estimates below fold these in.

| Phase | Passes | Opus 5 | Sonnet 5 | Haiku 4.5 |
|---|---|---|---|---|
| Per C1 pass | 1 | ≈$1.31 | ≈$0.52 | ≈$0.26 |
| Per C3 pass (larger input) | 1 | ≈$1.58 | ≈$0.63 | ≈$0.32 |
| P1 pilot (C1 × 1 model × 1 run) | 1 | — | ≈$0.52 | — |
| P2 main (C1+C2+C3 × 5 runs, per model) | 15 | ≈$21.5 | ≈$8.6 | ≈$4.3 |
| P3 repair C4 (≤3 calls/case × 5 runs, per model; context grows ≈1.6×) | ≤15 eq. | ≈$52 | ≈$21 | ≈$10 |

**Illustrative total** if the slate were {Opus 5, Sonnet 5, Haiku 4.5} for P2 and
{Opus 5, Sonnet 5} for P3: ≈ $34 (P2) + $73 (P3) + $1 (P1) ≈ **$108**; with the Batch API for
P1–P2, ≈ **$91**. A **hard cap of $150** is recommended; the runner must halt at the cap.

**Slate caveat (protocol consistency + conflict of interest).** The all-Anthropic table above
is illustrative only because Anthropic prices are the only ones verified offline in this
session. The frozen protocol (STUDY_PROTOCOL.md §4) requires models from **at least two
providers**; at authorization time, add at least one non-Anthropic model with its price page
(URL + retrieval date) and extend this table. Additionally, because the benchmark artifacts
were authored with Claude assistance, evaluating Claude models carries a
familiarity/conflict-of-interest concern that the paper must disclose; a
non-Anthropic-inclusive slate also mitigates it analytically.

## Verified prices and final slate (2026-09-01)

Prices re-verified on 2026-09-01 from official pages (URLs in `run_config.json`):
Anthropic — Claude Opus 5 $5/$25 (cache read $0.50/MTok), Claude Sonnet 5 $2/$10;
OpenAI — gpt-5.6-terra $2/$12 (cached input $0.20), gpt-5.6-luna $0.20/$1.20.
Slate (protocol §4 + A1): opus5 (frontier), sonnet5 + gpt-5.6-terra (mid, cross-vendor),
gpt-5.6-luna (small, non-authoring vendor). Prompt caching enabled (k=5 repeats of the same
prompt read at 0.1× input). Revised estimate for P1+P2+P3 with this slate: roughly $60–100
depending on model verbosity and repair rounds; the $150 hard cap is enforced per call by the
runner's spend ledger.

## Authorization checklist

- [x] Re-verify prices (2026-09-01; URLs in run_config.json).
- [ ] Replace heuristic token counts with provider `count_tokens` measurements (needs a live
      key; run automatically at P1 start).
- [x] Hard cap ($150) in runner config; halt path implemented (BudgetExceeded) and the
      mock end-to-end run exercised the ledger (36/36 pipeline validation, $0.00 spent).
- [x] Credentials via environment/Keychain only; runner startup scans repo for key patterns
      and aborts on any hit; sandbox probe verified (network denied, env scrubbed, oracle
      unreachable).
- [x] Written authorization recorded in `04_experiments/RUN_AUTHORIZATION.md`
      (2026-09-01, cap $150).
