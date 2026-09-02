"""BAT-02 reference solution: legacy batch runner error semantics (SYSTEM_OVERVIEW.md §7).

Sequential execution in list order; ABORT stops the schedule; CONTINUE logs BATCH_ROWSKIP
and proceeds; RETRY:n re-invokes up to n additional times then aborts if still failing.
The executor is injected and raises on failure; the runner never raises for job failures.
"""


def run_jobs(jobs, executor):
    log = []
    for job in jobs:
        on_error = job.get("on_error") or {}
        policy = on_error.get("policy", "ABORT")
        retries = int(on_error.get("retries", 0) or 0)
        max_attempts = retries + 1 if policy == "RETRY" else 1

        attempts = 0
        succeeded = False
        while attempts < max_attempts:
            attempts += 1
            try:
                executor(job)
                succeeded = True
                break
            except Exception:
                continue  # immediate re-run if attempts remain

        if succeeded:
            log.append({"name": job["name"], "attempts": attempts,
                        "outcome": "ok", "audits": []})
        elif policy == "CONTINUE":
            log.append({"name": job["name"], "attempts": attempts,
                        "outcome": "skip", "audits": ["BATCH_ROWSKIP"]})
        else:  # ABORT, or RETRY exhausted
            log.append({"name": job["name"], "attempts": attempts,
                        "outcome": "abort", "audits": []})
            break
    return log
