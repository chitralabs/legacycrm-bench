# SCR-01 Target Specification

Migrate the nightly CRMScript job `legacy/order_totals.crms` (language semantics in
`legacy/SEMANTICS_EXCERPT.md`) to the modern platform as **one Python module**
`migrated.py`. The legacy job iterates all orders; the modern service recomputes **one
order and its lines** per call (the caller supplies the rows).

## Required interface

```python
def recompute(order: dict, lines: list[dict]) -> tuple[dict, list[dict], list]: ...
```

- `order`: an ORD_HEADER row; `lines`: its ORD_LINE rows in input order. Numeric fields
  (`QTY`, `UNIT_PRC`, `EXT_AMT`, `DISC_PCT`, `TOT_AMT`) may be numbers or numeric strings;
  empty string / missing behaves as 0 (`NVL(x,0)` in the script).
- Returns `(new_order, new_lines, audits)` where `new_order`/`new_lines` are **new** dicts
  (inputs never mutated), `new_lines` preserves input order and length, and `audits` is a
  list of `(code, entity_id)` tuples.

## Required behavior (from order_totals.crms)

1. **Skip guard**: the legacy loop is `WHERE DEL_FLG = 'N' AND STAT_CD <> 'X'`. If the
   order is soft-deleted (`DEL_FLG == 'Y'`) or cancelled (`STAT_CD == 'X'`), return the
   order and lines unchanged (copies) with `audits == []`.
2. For each **live** line (`DEL_FLG <> 'Y'`): `EXT_AMT = NVL(QTY,0) * NVL(UNIT_PRC,0)`,
   rounded half-up to cents, stored as a float on the returned line. Soft-deleted lines
   are returned unchanged (their stale `EXT_AMT` is preserved) and excluded from the total.
3. `total` = sum of the recomputed live-line `EXT_AMT` values.
4. `TOT_AMT = total * (100 - NVL(DISC_PCT,0)) / 100`, **rounded half-up to cents**
   (e.g. 5.005 → 5.01, not banker's rounding), stored as a float on the returned order.
   Use exact decimal arithmetic; binary-float artifacts must not change the rounding.
5. Emit audit `("ORD_RETOTAL", <ORD_ID>)` **iff** the recomputed `TOT_AMT` differs
   *numerically* from the incoming `TOT_AMT` (the script's `IF ord.TOT_AMT <> discounted`;
   `"10.5"` equals `10.50`). Correcting a stale line `EXT_AMT` alone emits no audit.
6. No other audit codes are ever emitted.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
