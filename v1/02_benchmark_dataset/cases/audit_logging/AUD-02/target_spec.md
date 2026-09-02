# AUD-02 Target Specification

Migrate the Meridian CRM per-column audit event emitter (semantics:
`legacy/SEMANTICS_EXCERPT.md` = SYSTEM_OVERVIEW.md §8; audited columns:
`legacy/audit_config.cfg`; entity keys: `legacy/legacy_schema.sql`) to the modern platform as
**one Python module** `migrated.py`. The audited-column configuration is *baked into* the
module as part of the migration (it is static legacy configuration).

## Required interface

```python
def emit_audits(table: str, old: dict, new: dict, user: str, ts: str) -> list[dict]: ...
```

- `table`: legacy table name; `old`/`new`: pre- and post-update row images (dicts; missing
  keys behave as empty string); `user`: acting USR_ID; `ts`: injected event timestamp string
  (passed through verbatim — never read the wall clock).
- Returns the audit events for this UPDATE, as a list of dicts.

## Required behavior (SYSTEM_OVERVIEW.md §8 + artifacts)

1. **One event per changed audited column.** For the given `table`, consider exactly the
   columns listed for it in `audit_config.cfg`:
   - ACCT_MASTER: CRED_HOLD, CRED_LIMIT, OWNER_UID
   - OPP_MASTER: STAT_CD, AMT, OWNER_UID
   - CASE_MASTER: STAT_CD, SEV_CD
   - ORD_HEADER: STAT_CD, DISC_PCT
   - USR_MASTER: ROLE_ID, ACTIVE_FLG
   A table not in this list emits nothing (empty list).
2. **Change detection on stringified values.** A column is changed iff `str(old_value) !=
   str(new_value)`, where a missing key or `None` stringifies to `""`. Unchanged audited
   columns and changed *unaudited* columns emit nothing.
3. **Event order** follows the `audit_config.cfg` file order of that table's columns
   (e.g. an ACCT_MASTER update changing OWNER_UID and CRED_HOLD emits CRED_HOLD first).
4. **Event shape** — exactly these keys, mirroring the AUD_EVENT schema (EVT_ID is assigned by
   the store, not the emitter):
   - `"EVT_TS"`: the injected `ts`, verbatim.
   - `"EVT_CD"`: the fixed code `"COL_UPD"` (modern code for a column-level update event).
   - `"USR_ID"`: the acting user id, verbatim.
   - `"ENT_NAME"`: the table name.
   - `"ENT_ID"`: the row's primary-key value taken from `new` (fall back to `old` if missing),
     per the PK columns in `legacy_schema.sql`: ACCT_MASTER→ACCT_ID, OPP_MASTER→OPP_ID,
     CASE_MASTER→CASE_ID, ORD_HEADER→ORD_ID, USR_MASTER→USR_ID.
   - `"OLD_VAL"` / `"NEW_VAL"`: the stringified old/new column values (§8: "OLD_VAL/NEW_VAL as
     strings"; missing/None → `""`).

## Deliverable

- `migrated.py` only. Python ≥ 3.10, stdlib only, deterministic, no I/O, no network.
