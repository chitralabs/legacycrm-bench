# OpenAI Dry-Run Cost Estimate — LegacyCRM-Bench Experiments

Date: 2026-09-01 · Status: **APPROVED by project owner (see RUN_AUTHORIZATION.md); P1 executed (§7); P2/P3 in progress under the $150 cap.**

## 1. Authentication check (completed, free)

`models.list` succeeded with the key sourced in-memory from the user's shell profile
(never printed, logged, or written to any file; the repo credential-pattern scan is a runner
startup gate, and `v1/.gitignore` excludes `.env*`/key files). All three target models are
available on the account: `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna` (no dated snapshot
IDs exist for the 5.6 family; the runner records each response's resolved model string).
No Anthropic key exists on this machine → OpenAI-only slate per Protocol Amendment A3.

## 2. Benchmark size and measured inputs (exact prompt strings, chars÷4 heuristic)

36 cases / 521 acceptance tests. Prompt totals per full 36-case pass, measured over the
runner's actual `build_prompt` outputs (v2 measurement; the v1 figure of ~92k was a
double-count, corrected in ledger claim C011):

| Condition | Input tokens/pass (approx) |
|---|---|
| C1 zero-shot | 46,789 |
| C2 structured | 58,657 |
| C3 spec-retrieval | 97,522 |

Output is the main uncertainty (reasoning models bill hidden reasoning as output). Scenarios
per full pass: **LOW** = reference-sized 16,860; **CENTRAL** = 2× text + ~1k reasoning/case ≈
69,720; **HIGH** = 4× text + ~4k reasoning/case ≈ 211,440. The runner caps
`max_completion_tokens` at 16,000/call. The heuristic token counts are calibrated against
exact provider usage fields at the pilot.

## 3. Prices (verified 2026-09-01, https://developers.openai.com/api/docs/pricing)

| Model | Input $/MTok | Cached input | Output $/MTok |
|---|---|---|---|
| gpt-5.6-sol (frontier) | 4.00 | 0.40 | 20.00 |
| gpt-5.6-terra (mid) | 2.00 | 0.20 | 12.00 |
| gpt-5.6-luna (small) | 0.20 | 0.02 | 1.20 |

OpenAI auto-caches long prompt prefixes; the k=5 repeats of identical prompts run adjacently,
so runs 2–5 should read ~90% cached (input cost estimates below show uncached → cache-adjusted).

## 4. Dry-run estimate by phase, model, and condition

**P1 pilot** — gpt-5.6-terra × C1 × 1 run × 36 cases:
input $0.09; output LOW $0.20 / CENTRAL $0.84 / HIGH $2.54 → **≈ $0.30–2.60 total**.

**P2 main** — {sol, terra, luna} × {C1, C2, C3} × 5 runs (input/model: 1.015M uncached ≈
0.357M cache-adjusted full-price-equivalent; output/model: LOW 0.253M / CENTRAL 1.046M /
HIGH 3.172M):

| Model | Input (cached→uncached) | Out LOW | Out CENTRAL | Out HIGH | P2 total (central) |
|---|---|---|---|---|---|
| sol | $1.43→$4.06 | $5.06 | $20.92 | $63.43 | ≈ $22–25 |
| terra | $0.71→$2.03 | $3.03 | $12.55 | $38.06 | ≈ $13–15 |
| luna | $0.07→$0.20 | $0.30 | $1.25 | $3.81 | ≈ $1.4 |
| **P2 sum** | | **≈$11** | **≈$40** | **≈$110** | **≈ $37–41** |

**P3 agentic (C4)** — {sol, terra} × 5 runs, ≤2 redacted-feedback repairs on failing cases
(assumption: 40% of case-runs take one repair, 10% two; repair context grows by the previous
answer): CENTRAL ≈ **$21** (sol $13, terra $8); LOW ≈ $8; HIGH (every case repaired twice at
high output) ≈ $72.

## 5. Totals and safeguards

| Scenario | P1+P2+P3 |
|---|---|
| LOW | ≈ **$20** |
| CENTRAL | ≈ **$60–65** |
| HIGH | ≈ **$185 → capped at $150** |

- **Program-level maximum-spend safeguard (implemented, tested):** every call's cost is
  accrued from provider usage fields into `04_experiments/spend_ledger.json`; the runner
  refuses any call once `spent + worst_case_next ($3) > $150` and halts with a recorded
  `_halt` row. Exercised in the mock end-to-end run.
- **Descoping rule (pre-committed):** if the pilot lands in the HIGH output regime, before P2
  we reduce k=5→3 and/or drop C3 for sol, logged as a protocol amendment — the cap is never
  met by silently truncating data collection mid-phase.
- Every call preserves: exact model ID + resolved model string, execution timestamp, full
  prompt (SHA-256 + raw file), full raw response, and usage totals. Failed calls are recorded
  as `infra_error` — never fabricated.

## 6. Approval requested

Approving this estimate authorizes, in order: **P1 pilot (≈$0.30–2.60)** → pilot report and
recalibrated projection → **P2 + P3 (≈$60–65 central)** under the $150 hard cap and the
descoping rule. Reply with approval (or "pilot only") to proceed.


## 7. Pilot calibration (ACTUALS, 2026-09-01 — P1 executed after approval)

gpt-5.6-terra × C1 × 36 cases: **36/36 cases all-pass (521/521 tests)**, total cost
**$0.47** (36 calls; 53,230 real input tokens, 30,588 real output tokens
from provider usage fields). Real total cost came in below the LOW scenario. Calibration detail: the chars/4 heuristic
slightly UNDERestimated inputs (46.8k est. vs 53,230 actual per C1 pass, ~14% low), while
outputs were far smaller than the reasoning-heavy scenarios (30,588 actual vs 69,720
central) — the output term dominates cost, so the net effect is well below estimate. Revised full-protocol projection at pilot-observed rates:
P2 (3 models × C1–C3 × 5 runs) ≈ $20–30; P3 (C4, repairs rarely triggered at these pass
rates) ≈ $5–10; **grand total ≈ $25–40**, far under the $150 cap. The descoping rule is not
triggered. P1 gate passed: no harness or prompt defects (file extraction succeeded on 36/36).

Scientific note recorded at calibration time: terra saturates the benchmark zero-shot; the
remaining discrimination questions move to the small tier, run-to-run reliability, and cost —
which P2/P3 measure. This will be reported as found.


## 8. Final actuals (protocol complete, 2026-09-02)

All phases executed: pilot 36 calls; P2 1,620; P3 360 + 11 repairs; **total metered spend
$33.59** (vs. $60–65 central estimate; $150 cap never approached). One mid-run interruption:
the account's pre-existing credit balance exhausted at $17.77; the owner topped up and the
patched runner resumed with zero duplicated calls (resume-skip) and zero infrastructure
errors in the final disposition table.
