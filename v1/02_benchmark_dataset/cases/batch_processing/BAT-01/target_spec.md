# BAT-01 Target Specification

Migrate the legacy nightly batch schedule `legacy/batch_jobs.cfg` (semantics in
`legacy/SEMANTICS_EXCERPT.md` = SYSTEM_OVERVIEW.md §7) to the modern platform.

## Deliverables (both required)

1. **`schedule.json`** — the migrated schedule for the shipped `legacy/batch_jobs.cfg`:
   a JSON array, one object per JOB line, **in file order**.
2. **`migrated.py`** — the reusable parser used to produce it:

```python
def parse_schedule(cfg_text: str) -> list[dict]: ...
```

## Entry schema (exact keys, no extras)

```json
{"name": "<job name>", "at": "HH:MM", "script": "<script.crms>",
 "on_error": {"policy": "ABORT" | "CONTINUE" | "RETRY", "retries": <int>}}
```

- `retries` is an **integer**: `n` for `RETRY:n`, `0` for ABORT and CONTINUE.

## Required behavior

1. A line `JOB <name> AT <HH:MM> RUN <script> [ON_ERROR <clause>]` maps 1:1 to an entry;
   array order == file order (the scheduler runs jobs sequentially in file order, §7).
2. `ON_ERROR ABORT` → `{"policy": "ABORT", "retries": 0}`; `ON_ERROR CONTINUE` →
   `{"policy": "CONTINUE", "retries": 0}`; `ON_ERROR RETRY:n` →
   `{"policy": "RETRY", "retries": n}`.
3. **Default when the clause is absent**: the `ON_ERROR` clause is optional in the §7 line
   format. Because the jobs form a sequential nightly chain (§7: "jobs run sequentially in
   file order") where later jobs consume earlier jobs' outputs, the migration must default
   an absent clause to the strictest policy: `{"policy": "ABORT", "retries": 0}`.
4. Comment lines starting with `#` and blank lines are ignored (the shipped cfg begins
   with a `#` comment line).
5. `parse_schedule` applied to the shipped `legacy/batch_jobs.cfg` text must produce
   exactly the contents of `schedule.json` — no invented, dropped, or reordered jobs.

## Constraints

- Python ≥ 3.10, stdlib only, deterministic, no network. `migrated.py` performs no I/O
  itself (`parse_schedule` takes the text as an argument).
