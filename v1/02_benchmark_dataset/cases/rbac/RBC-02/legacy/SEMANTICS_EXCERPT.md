# Excerpt of legacy_system/SYSTEM_OVERVIEW.md (authoritative semantics)

## 5. RBAC — semantics

`role_permissions.csv` columns: `role_id,object,action,scope`.
Objects are entity names; actions in {READ, CREATE, UPDATE, DELETE, EXPORT}; scope in
{ALL, TEAM, OWN, NONE}. USR_MASTER.ROLE_ID assigns exactly one role. TEAM scope: user's
TEAM_CD must equal the record owner's TEAM_CD (owner = OWNER_UID column). OWN scope: OWNER_UID
must equal the user id. Entities whose physical table lacks a TEAM_CD column (e.g., ORD_HEADER) have the record's
team supplied by the application layer from the owner's USR_MASTER row (OWNER_UID -> TEAM_CD)
before the check runs, so scope checks always see a team attribute on the record image.
Permission checks deny by default: a missing (role, object, action) row
means NONE. Row-level rule: DELETE additionally requires the record to be soft-deletable
(DEL_FLG currently 'N'). The ADMIN role bypasses scope but not object/action rows (an ADMIN row
must still exist for the object/action; its scope is ignored and treated as ALL).

## 1. Entities and storage (relevant conventions)

- Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`.
- **Soft delete.** `DEL_FLG='Y'` rows are logically deleted; all reads must exclude them
  unless stated.
