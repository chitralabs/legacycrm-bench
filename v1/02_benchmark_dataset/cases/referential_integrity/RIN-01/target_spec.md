# RIN-01 Target Specification

Reimplement the contact-orphan pass of the nightly integrity check
(`legacy/integrity_check.crms`, first FOR EACH loop; semantics
`legacy/SEMANTICS_EXCERPT.md`) as **one Python module** `migrated.py`.

## Required interface

```python
def find_orphans(contacts: list[dict], accounts: list[dict]) -> list[str]: ...
```

`contacts` are CONT_MASTER rows, `accounts` are ACCT_MASTER rows (dicts of strings;
missing keys behave as empty string). Inputs may arrive in any order.

## Required behavior (must match the legacy batch check)

1. A row is **live** iff its `DEL_FLG` is not `'Y'` (blank means `N` per §1).
2. Only **live contacts** are examined; soft-deleted contacts are skipped entirely
   (they are never reported, even if their ACCT_ID dangles).
3. A live contact is an **orphan** iff `LOOKUP(ACCT_MASTER, ACCT_ID, cont.ACCT_ID,
   ACCT_ID) = ''`, i.e. there is **no live account** whose ACCT_ID equals the contact's
   ACCT_ID. Because LOOKUP sees live rows only, a contact pointing at a
   **soft-deleted account IS an orphan**. A blank/missing ACCT_ID matches no live row
   and is therefore an orphan.
4. Return the orphans' `CONT_ID` values ordered by **CONT_ID ascending** (the legacy
   FOR EACH iterates live rows in primary-key order), regardless of input order.
5. Pure function: inputs are not mutated; no I/O.

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no network.
