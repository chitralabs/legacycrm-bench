# Excerpts from SYSTEM_OVERVIEW.md (Meridian CRM 4.2, authoritative semantics)

## 1. Entities and storage (conventions, excerpt)

Schema: legacy SQL dialect (`VARCHAR2`, `NUMBER`, **no FK constraints** — referential
integrity is enforced by application code and nightly batch checks).

- **Soft delete.** `DEL_FLG='Y'` rows are logically deleted; all reads must exclude them
  unless stated. Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`.
- **Composite keys.** ORD_LINE key is (ORD_ID, LINE_NO).

Documented application behavior the modern FK graph must mirror:
- The nightly `integrity_check.crms` treats a contact or order pointing at a missing or
  soft-deleted account as an **orphan** (an error to be surfaced) — accounts with
  dependents are never silently removed → modern `ON DELETE RESTRICT` on
  CONT_MASTER.ACCT_ID and ORD_HEADER.ACCT_ID.
- The same script **soft-deletes order lines whose header is gone** (orphan lines are
  removed, not reported) → modern `ON DELETE CASCADE` on ORD_LINE.ORD_ID.

## 2. VRL — LOOKUP (excerpt)

`LOOKUP(TABLE, key_col, key_val, out_col)` returns the matching column value or empty
string **if no live row** — soft-deleted parents do not satisfy references, so rows
pointing at them must not be loaded into the modern store.
