# VAL-02 Target Specification

Migrate the five legacy VRL rules in `legacy/account_rules.vrl` (semantics:
`legacy/SEMANTICS_EXCERPT.md`) to the modern platform as **one Python module** `migrated.py`.
The interface is identical to VAL-01.

## Required interface

```python
def validate(record: dict, old: dict | None = None, event: str = "INSERT",
             today: str = "20260901") -> list[dict]: ...

def is_blocked(errors: list[dict]) -> bool: ...
```

- `record`: the post-write image of the ACCT_MASTER row; string values for text/code columns,
  numbers or numeric strings for NUMBER columns. Missing keys behave as empty string.
- `old`: pre-update image for `event="UPDATE"`; ignored for INSERT (where every `OLD.<col>`
  reference resolves to empty string / 0 in numeric context).
- `event`: `"INSERT"` or `"UPDATE"`; a rule runs only if the event is in its WHEN list
  (ACC-004 is UPDATE-only).
- `today`: injected current date (unused by these five rules but part of the fixed interface).

## Required behavior (must match legacy engine semantics exactly)

1. Evaluate every applicable rule in rule-file order; collect **all** failures.
2. Each failure appends `{"code": "<error code>", "message": "<message>", "severity": "BLOCK"|"WARN"}`.
3. `is_blocked(errors)` is True iff any failure has severity BLOCK.
4. Numeric coercion: empty string (and missing field) compares as 0 in numeric context;
   `NVL(x, d)` returns `d` when `x` is empty/missing/None. `LEN(x)` is string length
   (missing → 0).
5. Severity defaults to BLOCK; ACC-005 is WARN.
6. ACC-004 uses `OLD.CRED_HOLD`: it can only fail on UPDATE where the pre-image had
   `CRED_HOLD='Y'`, the new image has `'N'`, and `CRED_LIMIT <= 0` (blank coerces to 0,
   which is `<= 0`).

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
