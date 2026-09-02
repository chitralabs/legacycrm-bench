# SCR-03 Target Specification

Migrate the nightly CRMScript job `legacy/case_escalation.crms` (language semantics in
`legacy/SEMANTICS_EXCERPT.md`) to the modern platform as **one Python module**
`migrated.py`. The job scans support cases and posts `auto_escalate` workflow events for
overdue ones; the modern service returns the events instead of posting them.

## Required interface

```python
def escalate(cases: list[dict], today: str) -> list[dict]: ...
```

- `cases`: CASE_MASTER rows. `today`: injected current date as a `YYYYMMDD` string
  (replaces `TODAY()`; never read the wall clock).
- Returns the list of events to post, each exactly
  `{"workflow": "case_lifecycle", "entity_id": "<CASE_ID>", "event": "auto_escalate"}`,
  at most one per case, ordered by ascending `CASE_ID` (the legacy `FOR EACH` iterates
  live rows by primary key ascending) regardless of input order.

## Required behavior (from case_escalation.crms)

1. Only live cases are scanned (`DEL_FLG <> 'Y'`); soft-deleted cases never escalate.
2. New-case rule: `STAT_CD == 'N'` and `DATEDIFF(today, OPEN_DT) >= 2` → emit event.
   This rule does **not** look at `ESC_FLG`.
3. Assigned-case rule: `STAT_CD == 'A'` and `ESC_FLG != 'Y'` (blank/missing counts as not
   escalated) and `DATEDIFF(today, OPEN_DT) >= 7` → emit event.
4. Other statuses (P, R, X) never escalate, however old.
5. `DATEDIFF(d1, d2)` is **whole calendar days d1 − d2** (real date arithmetic across
   month/year boundaries, not string or integer subtraction), and **0 if either argument
   is the `00000000` sentinel** — so a case with a sentinel `OPEN_DT` is never overdue.
   Treat an empty/missing `OPEN_DT` like the sentinel (uninitialized values read as empty
   string; there is no date to diff). A future `OPEN_DT` gives a negative day count and
   never escalates.
6. Day boundaries are exact: 1 day old is not overdue for rule 2; exactly 2 days is.
   6 days is not overdue for rule 3; exactly 7 days is.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
