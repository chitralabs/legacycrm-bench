# BIZ-01 Target Specification

Migrate the legacy credit-hold release guard (rule ACC-004 in `legacy/account_rules.vrl`;
audit code from `legacy/credit_hold_sweep.crms`; semantics `legacy/SEMANTICS_EXCERPT.md`)
to a modern account service in **one Python module** `migrated.py`.

## Required interface

```python
class BusinessRuleViolation(Exception):
    code: str      # legacy error code
    message: str   # legacy error message

def release_credit_hold(account: dict) -> tuple[dict, list[dict]]: ...
```

`account` is an ACCT_MASTER row (dict of strings/numbers; missing keys behave as empty
string). Returns `(updated_account, audits)` where `updated_account` is a **new** dict
and `audits` is a list of `{"code": str, "entity_id": str}` events.

## Required behavior

1. **Not on hold** (`CRED_HOLD` != 'Y'; blank means 'N'): the release is vacuous —
   return an unchanged copy of the account and an empty audit list. (The legacy rule
   only fires on a Y→N transition; a no-op update raises nothing and audits nothing.)
2. **On hold, CRED_LIMIT <= 0** (empty/missing coerces to 0 per legacy numeric
   semantics): raise `BusinessRuleViolation` with `code="E1004"` and
   `message="Cannot release credit hold with zero credit limit"`. The account is not
   modified.
3. **On hold, CRED_LIMIT > 0**: return a copy with `CRED_HOLD='N'` (no other field
   changed) and exactly one audit event
   `{"code": "CRED_HOLD_OFF", "entity_id": <ACCT_ID>}` (the documented legacy audit
   code for a hold release).
4. Pure: the input dict is never mutated.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
