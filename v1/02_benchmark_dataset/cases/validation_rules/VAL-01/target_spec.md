# VAL-01 Target Specification

Migrate the seven legacy VRL rules in `legacy/opportunity_rules.vrl` (semantics:
`legacy/SEMANTICS_EXCERPT.md`) to the modern platform as **one Python module** `migrated.py`.

## Required interface

```python
def validate(record: dict, old: dict | None = None, event: str = "INSERT",
             today: str = "20260901") -> list[dict]: ...

def is_blocked(errors: list[dict]) -> bool: ...
```

- `record`: the post-write image of the OPP_MASTER row; string values for text/date/code
  columns, numbers or numeric strings for NUMBER columns. Missing keys behave as empty string.
- `old`: pre-update image for `event="UPDATE"`; ignored for INSERT (where every `OLD.<col>`
  reference resolves to empty string / 0 in numeric context).
- `event`: `"INSERT"` or `"UPDATE"`; a rule runs only if the event is in its WHEN list.
- `today`: injected current date `YYYYMMDD` (replaces `TODAY()`; never read the wall clock).

## Required behavior (must match legacy engine semantics exactly)

1. Evaluate every applicable rule in rule-file order; collect **all** failures (no stopping at
   the first BLOCK failure).
2. Each failure appends `{"code": "<error code>", "message": "<message>", "severity": "BLOCK"|"WARN"}`.
3. `is_blocked(errors)` is True iff any failure has severity BLOCK.
4. Numeric coercion: empty string (and missing field) compares as 0 in numeric context;
   numeric strings compare numerically. `NVL(x, d)` returns `d` when `x` is empty/missing/None.
5. Dates compare lexicographically as `YYYYMMDD` strings, except the `00000000` sentinel:
   any ordering comparison involving it is FALSE; equality to the literal `'00000000'` is the
   only true comparison against it.
6. Severity defaults to BLOCK; OPP-007 is WARN.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
