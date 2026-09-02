# BAT-02 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from the batch
semantics in `legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §7) applied to the
schedule schema of `legacy/batch_jobs.cfg`. No LLM output was used to produce
expectations. Test executors are deterministic scripted callables that fail on
predetermined attempt numbers. Derivations:

1. All jobs succeed: §7 sequential order → log has one entry per job, in list order,
   each {attempts 1, outcome "ok", audits []}; the executor sees the jobs in list order.
2. ABORT job fails: the failing job logs {attempts 1, outcome "abort"}; "jobs run
   sequentially" with the strictest policy → the schedule stops: later jobs have no log
   entry and the executor records show no invocation for them (negative expectation).
3. CONTINUE job fails: §7 "CONTINUE skips the failing row and logs BATCH_ROWSKIP" →
   entry {attempts 1, outcome "skip", audits ["BATCH_ROWSKIP"]} and the next job still
   runs (its entry follows with outcome "ok").
4. RETRY:2, executor fails twice then succeeds: §7 "re-runs the whole script up to n
   times" → invocations 1 (fail) + 2 re-runs; success on the 3rd → attempts 3, outcome
   "ok". No BATCH_ROWSKIP is logged for retried-then-successful jobs.
5. RETRY:2, executor always fails: 1 + 2 = 3 invocations, still failing → the job aborts
   the schedule (RETRY exhausts into the sequential default): attempts 3, outcome
   "abort", later jobs unattempted.
6. RETRY:2, executor succeeds immediately: no failure → no re-runs → attempts 1,
   outcome "ok" (retries are only spent on failures).
7. RETRY:1 failing both attempts: attempts 2 (1 + 1), abort.
8. Two CONTINUE failures in a row: both log BATCH_ROWSKIP and the following job still
   runs — CONTINUE never stops the schedule.
9. A successful CONTINUE job logs no BATCH_ROWSKIP (audit only accompanies a failure).
10. attempts == exact executor invocation count per job, verified by counting calls in
    the scripted executor (rule 6 of target_spec).
11. The runner never lets the executor's exception propagate (a failed ABORT schedule
    still returns a log; no raise).
12. Log entries appear only for attempted jobs: after an abort at index i, the log length
    is i+1.
