# RBC-01 Target Specification

Migrate the Meridian CRM permission check (semantics: `legacy/SEMANTICS_EXCERPT.md` = SYSTEM_OVERVIEW.md
§5) to the modern platform as **one Python module** `migrated.py`. This case focuses on the scope
model (ALL / TEAM / OWN / NONE) and deny-by-default; the full §5 semantics (including the ADMIN
override and the DELETE row-level rule) still apply and are stated below for completeness.

## Required interface

```python
def can(user: dict, action: str, object: str, record: dict, role_rows: list[dict]) -> bool: ...
```

- `user`: dict with at least `USR_ID`, `ROLE_ID`, `TEAM_CD` (strings; missing key behaves as `""`).
- `action`: one of `READ`, `CREATE`, `UPDATE`, `DELETE`, `EXPORT`.
- `object`: legacy entity/table name (e.g. `ACCT_MASTER`).
- `record`: dict with at least `OWNER_UID`, `TEAM_CD`, `DEL_FLG` (missing key behaves as `""`).
  `record["TEAM_CD"]` is the record owner's team (denormalized owner team, as stored on every
  ownable legacy table).
- `role_rows`: the permission matrix as a list of dicts with keys `role_id`, `object`, `action`,
  `scope` (i.e. `csv.DictReader` rows of `role_permissions.csv` or a hand-crafted matrix).
- Returns a strict `bool`.

## Required behavior (SYSTEM_OVERVIEW.md §5, §1)

1. **Deny by default.** If no row matches (`role_id == user's ROLE_ID`, `object`, `action`)
   exactly, the decision is deny (missing row means scope NONE). Unknown/blank roles therefore
   always deny.
2. Scope of the matching row decides:
   - `NONE` → deny.
   - `ALL` → allow (subject to rule 4).
   - `TEAM` → allow iff `user["TEAM_CD"] == record["TEAM_CD"]` (missing keys compare as `""`).
   - `OWN` → allow iff `record["OWNER_UID"] == user["USR_ID"]`.
3. **ADMIN override.** If the user's role is `ADMIN` and the row exists, the row's scope is
   ignored and treated as `ALL`. No row → deny, exactly as for any other role.
4. **DELETE row-level rule.** `DELETE` additionally requires the record to be currently
   soft-deletable: `DEL_FLG` must be `'N'` (blank counts as `'N'` per the §1 blank-boolean
   convention); `DEL_FLG='Y'` denies DELETE regardless of scope or role.
5. No other action is affected by `DEL_FLG` (the §5 row-level rule is stated for DELETE only;
   read-visibility filtering of soft-deleted rows is a query concern outside `can()`).

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
