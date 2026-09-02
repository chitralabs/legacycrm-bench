# ERR-01 Target Specification

Migrate the legacy CRMScript division-by-zero quirk (semantics: `legacy/SEMANTICS_EXCERPT.md`
= SYSTEM_OVERVIEW.md §4; example expression context: `legacy/order_totals.crms`) to the modern
platform as **one Python module** `migrated.py`. The quirk is preserved, not modernized:
"Numeric division by zero yields 0 and logs audit `SCRIPT_DIV0`".

## Required interface

```python
def safe_div(a, b) -> tuple[float, list[str]]: ...
```

- `a`, `b`: numbers, numeric strings, empty strings, or None. Legacy numeric coercion applies
  to both operands: empty string, missing/None coerce to 0 in numeric context (§2/§4);
  numeric strings coerce to their numeric value.
- Returns `(value, audits)` where `audits` is a list of audit codes emitted by this evaluation.

## Required behavior (SYSTEM_OVERVIEW.md §4)

1. Non-zero divisor: `value = a / b` as a float; `audits == []`.
2. Divisor coercing to 0 (including `0`, `0.0`, `""`, `None`, `"0"`): `value == 0.0` and
   `audits == ["SCRIPT_DIV0"]` — exactly one code per division.
3. **No exception ever propagates** from `safe_div` for any operand combination above; the
   legacy engine never raised on division by zero and the migration must not either.
4. The result value on division by zero is the number 0 (not None, not NaN, not infinity).

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
