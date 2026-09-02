# BIZ-02 Target Specification

Migrate the legacy discount policy (rules ORD-001 and ORD-002 in
`legacy/order_rules.vrl`; semantics `legacy/SEMANTICS_EXCERPT.md`) to a modern order
service in **one Python module** `migrated.py`.

## Required interface

```python
class BusinessRuleViolation(Exception):
    code: str
    message: str

def set_discount(order: dict, pct, user_id: str, users: list[dict]) -> dict: ...
```

`order` is an ORD_HEADER row; `pct` is the requested discount percent (number or
numeric string); `user_id` identifies the acting user (the order's owner performing the
update); `users` is the USR_MASTER table as a list of row dicts.

## Required behavior (checks in legacy rule-file order)

1. **Range (ORD-001):** if not `0 <= pct <= 100`, raise `BusinessRuleViolation` with
   `code="E5001"`, `message="Discount out of range"`. Both boundaries are inclusive.
   This check runs first (rule-file order), so an out-of-range discount reports E5001
   even when the role check would also fail.
2. **Role (ORD-002):** if `pct > 20` (strictly), resolve the user's role with legacy
   LOOKUP semantics: the `ROLE_ID` of the first **live** (`DEL_FLG` != 'Y'; blank
   means 'N') users row whose `USR_ID` equals `user_id`, else `""`. Unknown and
   soft-deleted users therefore have role `""`. If the role is neither `'MGR'` nor
   `'ADMIN'`, raise `BusinessRuleViolation` with `code="E5002"`,
   `message="Discount over 20 percent requires manager role"`.
   `ACTIVE_FLG` plays no part (LOOKUP consults soft-delete only).
   A discount of exactly 20 requires no role at all.
3. On success, return a **new** order dict identical to the input except `DISC_PCT`
   set to `pct` (as passed). The input `order` and `users` are never mutated.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
