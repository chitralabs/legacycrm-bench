# Excerpts from SYSTEM_OVERVIEW.md (Meridian CRM 4.2, authoritative semantics)

## 1. Entities and storage (conventions, excerpt)

- **Soft delete.** `DEL_FLG='Y'` rows are logically deleted; all reads must exclude them
  unless stated. Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`.

## 2. VRL — semantics (excerpt)

- `LOOKUP(TABLE, key_col, key_val, out_col)` returns the matching column value **or
  empty string if no live row**. (An unknown or soft-deleted user therefore has role
  `''` — which is neither 'MGR' nor 'ADMIN'.)
- Rules run in file order; a rule *passes* when its expr evaluates TRUE; on failure,
  SEVERITY BLOCK (default) rejects the write with the error code.
- Comparisons are on exact values; numeric comparisons compare numerically.

Rules in scope (`order_rules.vrl`):
- ORD-001 (INSERT, UPDATE): `DISC_PCT >= 0 AND DISC_PCT <= 100` else
  `E5001 "Discount out of range"`.
- ORD-002 (UPDATE): fails iff `DISC_PCT > 20` and the owner's looked-up ROLE_ID is
  neither 'MGR' nor 'ADMIN' → `E5002 "Discount over 20 percent requires manager role"`.
  The boundary is **strictly greater than 20**: exactly 20 needs no role.

USR_MASTER columns (legacy_schema.sql): USR_ID (PK), ROLE_ID, ACTIVE_FLG, DEL_FLG.
LOOKUP consults DEL_FLG only (live rows); ACTIVE_FLG is not part of LOOKUP semantics.
