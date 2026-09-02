# Excerpts from SYSTEM_OVERVIEW.md (Meridian CRM 4.2, authoritative semantics)

## 1. Entities and storage (conventions, excerpt)

Schema: legacy SQL dialect with **no FK constraints** — referential integrity is enforced
by application code and nightly batch checks (`integrity_check.crms`).

- **Soft delete.** `DEL_FLG='Y'` rows are logically deleted; all reads must exclude them
  unless stated. Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`.

## 2. VRL — LOOKUP (excerpt)

`LOOKUP(TABLE, key_col, key_val, out_col)` returns the matching column value **or empty
string if no live row** (soft-deleted rows are invisible to LOOKUP).

## 4. CRMScript — semantics (excerpt)

`FOR EACH row IN <TABLE> [WHERE expr] ... NEXT` iterates **live rows, ordered by primary
key ascending**.
