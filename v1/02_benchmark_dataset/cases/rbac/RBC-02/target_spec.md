# RBC-02 Target Specification

Migrate the Meridian CRM permission check (semantics: `legacy/SEMANTICS_EXCERPT.md` =
SYSTEM_OVERVIEW.md §5, §1) as **one Python module** `migrated.py`. This case focuses on the two
semantics most often botched by naive migrations: the **ADMIN override** (scope bypass without
row bypass) and the **DELETE row-level rule** (record must be currently soft-deletable).

## Required interface

```python
def can(user: dict, action: str, object: str, record: dict, role_rows: list[dict]) -> bool: ...
```

Parameter shapes are identical to RBC-01:
- `user`: `{"USR_ID", "ROLE_ID", "TEAM_CD"}` (strings; missing key behaves as `""`).
- `action` ∈ {READ, CREATE, UPDATE, DELETE, EXPORT}; `object` is a legacy table name.
- `record`: `{"OWNER_UID", "TEAM_CD", "DEL_FLG"}` (missing key behaves as `""`);
  `record["TEAM_CD"]` is the record owner's team.
- `role_rows`: list of dicts with keys `role_id`, `object`, `action`, `scope`.
- Returns a strict `bool`.

## Required behavior (SYSTEM_OVERVIEW.md §5, §1)

1. Deny by default: no matching (role, object, action) row → deny. **This applies to ADMIN
   too**: the ADMIN role bypasses *scope*, never the row requirement. An action/object pair with
   no ADMIN row is denied for ADMIN users — widening ADMIN to "everything" is a migration bug.
2. For a matching row with the user's role equal to `ADMIN`, the row's scope value is ignored
   and treated as `ALL` (whatever the row says).
3. Non-ADMIN scope semantics as in §5: ALL grants; TEAM requires equal owner team; OWN requires
   record OWNER_UID == user id; NONE denies.
4. **DELETE row-level rule**: DELETE is additionally allowed only when the record's `DEL_FLG` is
   currently `'N'`. Blank/missing `DEL_FLG` counts as `'N'` (§1: blank CHAR(1) boolean means
   `N`). `DEL_FLG='Y'` (already soft-deleted) denies DELETE for every role including ADMIN.
5. The DEL_FLG rule applies to DELETE only; other actions ignore `DEL_FLG` in the permission
   decision (§5 states the row-level rule for DELETE; read-visibility of soft-deleted rows is a
   query concern outside `can()`).

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
