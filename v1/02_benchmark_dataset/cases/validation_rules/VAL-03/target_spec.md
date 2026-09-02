# VAL-03 Target Specification

Migrate the five legacy VRL order rules in `legacy/order_rules.vrl` (semantics:
`legacy/SEMANTICS_EXCERPT.md`; looked-up tables: `legacy/lookup_tables.sql`) to the modern
platform as **one Python module** `migrated.py`. The rules span two tables (ORD-001..003 on
ORD_HEADER, ORD-004..005 on ORD_LINE), so the interface takes the rule table explicitly.

## Required interface

```python
def validate(record: dict, old: dict | None = None, event: str = "INSERT",
             tables: dict | None = None, table: str = "ORD_HEADER") -> list[dict]: ...

def is_blocked(errors: list[dict]) -> bool: ...
```

- `record` / `old` / `event`: as in VAL-01/VAL-02 (missing keys behave as empty string;
  `OLD.<col>` is empty on INSERT; a rule runs only if `event` is in its WHEN list).
- `tables`: dict of **in-memory tables**, e.g.
  `{"USR_MASTER": [ {row}, ... ], "PROD_MASTER": [ {row}, ... ]}` with string values.
  `None` behaves as no tables at all.
- `table`: `"ORD_HEADER"` or `"ORD_LINE"`; only the rules defined ON that table run
  (in rule-file order among themselves).

## LOOKUP semantics (must match the legacy engine exactly)

`LOOKUP(TABLE, key_col, key_val, out_col)`:
1. Scans `tables[TABLE]` for rows whose `key_col` equals `key_val`.
2. **Ignores soft-deleted rows** (`DEL_FLG == 'Y'`) — LOOKUP sees live rows only.
3. Returns the first matching live row's `out_col` value; returns `""` (empty string) when
   there is no live match, when the table is absent, or when `tables` is `None`.

Consequences the migration must preserve:
- ORD-002 (UPDATE only): with `DISC_PCT > 20`, the rule fails unless the owner's looked-up
  role is `'MGR'` or `'ADMIN'`. An unknown or soft-deleted owner looks up as `""`, which is
  neither, so the rule **fails**. `DISC_PCT = 20` exactly does not trigger the guard.
- ORD-005 (INSERT only): fails when the product is missing, soft-deleted, or has
  `ACTIVE_FLG != 'Y'` (all three look up as something ≠ 'Y').

## Required behavior

1. Applicable rules run in rule-file order; **all** failures are collected.
2. Each failure appends `{"code", "message", "severity"}` with the verbatim legacy values;
   all five rules default to severity BLOCK.
3. `is_blocked(errors)` is True iff any failure has severity BLOCK.
4. Numeric coercion: empty string / missing field compares as 0 (so blank DISC_PCT passes
   ORD-001 and blank QTY fails ORD-004).

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
