# BAT-02 Target Specification

Migrate the legacy batch scheduler's **error-handling runner semantics**
(`legacy/batch_jobs.cfg`, semantics in `legacy/SEMANTICS_EXCERPT.md` = SYSTEM_OVERVIEW.md
§7) to the modern platform as **one Python module** `migrated.py`.

## Required interface

```python
def run_jobs(jobs: list[dict], executor) -> list[dict]: ...
```

- `jobs`: schedule entries in run order, each
  `{"name": str, "at": "HH:MM", "script": str,
    "on_error": {"policy": "ABORT"|"CONTINUE"|"RETRY", "retries": int}}`
  (the schema produced by the BAT-01 migration).
- `executor`: injected callable; `executor(job)` runs one attempt of the job's script and
  **raises an exception on failure** (any Exception; no exception means success). The
  runner itself must never raise because a job failed.
- Returns the run log: one dict per job **attempted**, in run order:
  `{"name": str, "attempts": int, "outcome": "ok"|"skip"|"abort", "audits": list[str]}`.

## Required behavior (§7: jobs run sequentially in file order)

1. Jobs are executed strictly sequentially in list order; `executor` is never called for a
   job after the schedule has aborted.
2. Success (no exception): outcome `"ok"`, `audits == []`, proceed to the next job.
3. `ABORT` policy, attempt fails: outcome `"abort"`, `attempts == 1`, `audits == []`,
   and the **whole schedule stops** — later jobs get no log entry and no execution.
4. `CONTINUE` policy, attempt fails: log `"BATCH_ROWSKIP"` in `audits`, outcome `"skip"`,
   `attempts == 1`, and **proceed** to the next job (§7: "CONTINUE skips the failing row
   and logs BATCH_ROWSKIP").
5. `RETRY` policy with `retries == n`: on failure re-invoke the executor up to **n
   additional times** (§7: "re-runs the whole script up to n times"; total invocations ≤
   n+1). First success stops retrying: outcome `"ok"`, `attempts` = the number of
   invocations actually made. If all n+1 attempts fail, the job aborts the schedule like
   rule 3: outcome `"abort"`, `attempts == n + 1`, `audits == []`, stop.
6. `attempts` always equals the exact number of `executor` invocations for that job.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network, no
  sleeping/backoff (retries are immediate).
