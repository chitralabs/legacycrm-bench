# RBC-03 Target Specification

Migrate the entire Meridian CRM permission matrix (`legacy/role_permissions.csv`, semantics:
`legacy/SEMANTICS_EXCERPT.md` = SYSTEM_OVERVIEW.md §5, §1) to a modern **declarative policy
document plus enforcement module**. The migration must be *decision-for-decision equivalent* to
the legacy semantics over all users, records, objects, and actions; in particular it must not
widen any privilege.

## Deliverables (exactly two files)

1. `policy.json` — the modern policy document. Exact schema:

```json
{
  "version": 1,
  "default": "deny",
  "admin_role": "ADMIN",
  "delete_requires_live_record": true,
  "grants": [
    {"role": "ADMIN", "object": "ACCT_MASTER", "action": "READ", "scope": "ALL"},
    ...
  ]
}
```

- `grants` contains **one entry per data row of `role_permissions.csv`, in file order** — no
  additions, no omissions, no scope changes. `role`/`object`/`action`/`scope` are verbatim
  matrix values (scope ∈ {ALL, TEAM, OWN, NONE}).
- `default` must be the string `"deny"`.

2. `migrated.py` — enforcement module reading `policy.json` from **its own directory**
   (`Path(__file__).parent / "policy.json"`), exposing:

```python
def load_policy() -> dict: ...
def can(user: dict, action: str, object: str, record: dict) -> bool: ...
```

- `user`: `{"USR_ID", "ROLE_ID", "TEAM_CD"}`; `record`: `{"OWNER_UID", "TEAM_CD", "DEL_FLG"}`
  (missing keys behave as `""`; `record["TEAM_CD"]` is the record owner's team).
- Returns a strict `bool`.

## Required decision semantics (SYSTEM_OVERVIEW.md §5, §1)

1. Deny by default: no grant matching (user's role, object, action) → deny (unknown roles deny).
2. Scope of the matching grant: `ALL` → allow; `TEAM` → user TEAM_CD == record TEAM_CD;
   `OWN` → record OWNER_UID == user USR_ID; `NONE` → deny.
3. ADMIN (the `admin_role`) bypasses scope but not the grant requirement: with a matching grant
   its scope is treated as `ALL`; without one, deny.
4. DELETE additionally requires record `DEL_FLG` currently `'N'` (blank counts as `'N'` per §1);
   the rule applies to DELETE only.

## Equivalence obligation

The acceptance tests enumerate several hundred (user, record, object, action) decision tuples
built from the legacy matrix and hand-crafted fixtures, evaluate the documented legacy semantics
independently, and require the modern `can()` to agree on **every** tuple. Any tuple where the
modern stack allows and legacy denies (privilege widening) is a security failure. A scan test
additionally requires that `policy.json` grants exactly the legacy matrix rows.

## Constraints

Python ≥ 3.10, stdlib only, deterministic, no network; the only file I/O permitted is reading
`policy.json` from the module's own directory.
