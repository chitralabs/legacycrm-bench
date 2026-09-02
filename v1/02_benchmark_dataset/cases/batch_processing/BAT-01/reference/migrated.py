"""BAT-01 reference solution: batch_jobs.cfg parser (SYSTEM_OVERVIEW.md §7).

Line format: JOB <name> AT <HH:MM> RUN <script.crms> [ON_ERROR <ABORT|CONTINUE|RETRY:n>]
Absent ON_ERROR defaults to ABORT (strictest policy; the nightly jobs form a sequential
chain). Comment (#) and blank lines are ignored. No I/O: the caller supplies the text.
"""


def parse_schedule(cfg_text):
    jobs = []
    for raw in cfg_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        toks = line.split()
        if len(toks) < 6 or toks[0].upper() != "JOB" or toks[2].upper() != "AT" \
                or toks[4].upper() != "RUN":
            continue
        name, at, script = toks[1], toks[3], toks[5]
        policy, retries = "ABORT", 0  # default when the optional clause is absent
        if len(toks) >= 8 and toks[6].upper() == "ON_ERROR":
            clause = toks[7].upper()
            if clause.startswith("RETRY:"):
                policy, retries = "RETRY", int(clause.split(":", 1)[1])
            else:
                policy = clause
        jobs.append({"name": name, "at": at, "script": script,
                     "on_error": {"policy": policy, "retries": retries}})
    return jobs
