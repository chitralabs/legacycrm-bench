# BAT-01 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/batch_jobs.cfg` under the batch semantics in `legacy/SEMANTICS_EXCERPT.md`
(= SYSTEM_OVERVIEW.md §7). No LLM output was used to produce expectations. Derivations:

1. The shipped cfg has one `#` comment line and five JOB lines. Reading them off in file
   order gives exactly:
   1. `integrity_check`, at `01:00`, script `integrity_check.crms`, `ON_ERROR CONTINUE`
      → policy CONTINUE, retries 0.
   2. `credit_hold_sweep`, at `01:30`, script `credit_hold_sweep.crms`, `ON_ERROR ABORT`
      → policy ABORT, retries 0.
   3. `order_totals`, at `02:00`, script `order_totals.crms`, `ON_ERROR RETRY:2`
      → policy RETRY, retries 2.
   4. `case_escalation`, at `02:30`, script `case_escalation.crms`, `ON_ERROR CONTINUE`
      → policy CONTINUE, retries 0.
   5. `dw_export`, at `03:00`, script `dw_export.crms`, `ON_ERROR RETRY:1`
      → policy RETRY, retries 1.
   `schedule.json` must equal this array, in this order (§7: jobs run sequentially in
   file order, so order is semantic and must be preserved).
2. `retries` values are integers because RETRY:n's n is a count of re-runs ("re-runs the
   whole script up to n times"); ABORT/CONTINUE re-run nothing → 0.
3. Default-ABORT (target_spec rule 3): `parse_schedule("JOB x AT 04:00 RUN x.crms")` —
   the optional clause is absent → `{"policy": "ABORT", "retries": 0}`. Derived from the
   §7 optional-clause line format plus the sequential-chain safety argument stated in
   target_spec; tested through the parser since the shipped cfg spells every clause out.
4. Comment/blank handling: a cfg text of comment + blank + one JOB line parses to exactly
   one entry (the shipped cfg itself starts with a comment line, so this is required to
   get five entries rather than an error).
5. Parser/artifact consistency: `parse_schedule(text of legacy/batch_jobs.cfg)` must equal
   the deserialized `schedule.json` (rule 5 of target_spec).
6. Negative expectation: exactly the five job names above appear — a migration that
   invents, drops, or duplicates a job fails.
