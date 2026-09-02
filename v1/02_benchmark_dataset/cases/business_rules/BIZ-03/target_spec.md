# BIZ-03 Target Specification

Migrate the interacting invoiced-order rules — validation rule ORD-003
(`legacy/order_rules.vrl`), the `I -> X` workflow transition
(`legacy/order_fulfilment.xml`), and the total recompute (`legacy/order_totals.crms`) —
into **one Python module** `migrated.py`. A migration that preserves only the workflow
actions, or only the validation rule, or only the recompute, must fail: the three rules
constrain each other.

## Required interface

```python
class BusinessRuleViolation(Exception):
    code: str
    message: str

def transition_invoiced(order: dict, new_status: str) -> tuple[dict, list[str], list[str]]: ...
def recompute_total(order: dict, lines: list[dict]) -> tuple[dict, list[dict], list[str]]: ...
```

## `transition_invoiced(order, new_status) -> (order, audits, notifies)`

Handles status changes of an **invoiced** order (`STAT_CD == 'I'`); raise `ValueError`
if called with a non-invoiced order (programming error, not a business violation).

1. `new_status == 'X'` (cancel): return a new order with `STAT_CD='X'`,
   `audits == ["ORD_CANC_INV"]`, `notifies == ["credit_note"]` (the workflow's I→X
   actions, in document order).
2. `new_status == 'I'`: vacuous update — unchanged copy, `[]`, `[]`.
3. Any other status (`'E'`, `'A'`, `'S'`, anything else): raise
   `BusinessRuleViolation` with `code="E5003"`,
   `message="Invoiced order can only be cancelled"` (rule ORD-003).

## `recompute_total(order, lines) -> (order, lines, audits)`

Modern recompute of one order's totals, per `order_totals.crms`, with one deliberate
modernization: **invoiced totals are frozen** — the amount invoiced is the amount owed,
so a line change after invoicing must not alter the header.

1. If `order["STAT_CD"]` is `'I'` **or** `'X'`: return unchanged copies of the order
   and lines with `audits == []` (frozen / skipped; nothing recomputed, no audit).
2. Otherwise (E/A/S): for each **live** line (`DEL_FLG` != 'Y'; blank means 'N'):
   `EXT_AMT = NVL(QTY,0) * NVL(UNIT_PRC,0)` rounded half-up to cents (float, 2
   decimals). Soft-deleted lines are copied through untouched and excluded from the
   total.
3. `TOT_AMT = (sum of live EXT_AMT) * (100 - NVL(DISC_PCT,0)) / 100`, rounded
   **half-up** to cents on the decimal value (e.g. 5.005 → 5.01), as a float.
4. `audits == ["ORD_RETOTAL"]` iff the recomputed TOT_AMT differs numerically from the
   stored one (empty/missing compares as 0); otherwise `[]`.
5. Both functions are pure: inputs are never mutated; returned rows are new objects.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
