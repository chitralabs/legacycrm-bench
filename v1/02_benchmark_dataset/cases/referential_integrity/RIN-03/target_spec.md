# RIN-03 Target Specification

Replace the legacy application-enforced integrity (`legacy/legacy_schema_excerpt.sql`,
`legacy/integrity_check.crms`, semantics `legacy/SEMANTICS_EXCERPT.md`) with **declared
foreign keys** in SQLite. Two deliverables:

## Deliverable 1: `modern_schema.sql`

SQLite DDL for exactly four tables, keeping the legacy table and column names but with
real constraints. Soft delete is retired: the token `DEL_FLG` must not appear anywhere
in the delivered DDL file — not as a column, not in comments (deletion authority is the
FK graph).

- `ACCT_MASTER(ACCT_ID PK, ACCT_NM NOT NULL, ACCT_TYP, REGION_CD, ANN_REV, CURR_CD, CRED_LIMIT, CRED_HOLD, CREATE_DT)`
- `CONT_MASTER(CONT_ID PK, ACCT_ID NOT NULL, FRST_NM, LAST_NM NOT NULL, EMAIL_TX, PREF_CH, OPTOUT_FLG)`
  with `FOREIGN KEY (ACCT_ID) REFERENCES ACCT_MASTER(ACCT_ID) ON DELETE RESTRICT`
- `ORD_HEADER(ORD_ID PK, ACCT_ID NOT NULL, ORD_DT, STAT_CD, DISC_PCT, TOT_AMT)`
  with `FOREIGN KEY (ACCT_ID) REFERENCES ACCT_MASTER(ACCT_ID) ON DELETE RESTRICT`
- `ORD_LINE(ORD_ID NOT NULL, LINE_NO NOT NULL, PROD_ID, QTY, UNIT_PRC, EXT_AMT, PRIMARY KEY (ORD_ID, LINE_NO))`
  with `FOREIGN KEY (ORD_ID) REFERENCES ORD_HEADER(ORD_ID) ON DELETE CASCADE`

Delete actions mirror documented app behavior (SEMANTICS_EXCERPT): accounts with
dependents are protected (**RESTRICT**, declared explicitly — not left as implicit
NO ACTION), while deleting an order header removes its lines (**CASCADE**, exactly what
`integrity_check.crms` does to orphan lines). The DDL must apply cleanly with
`sqlite3.Connection.executescript` under `PRAGMA foreign_keys=ON`.

## Deliverable 2: `migrated.py`

```python
def load(conn: sqlite3.Connection, tables: dict[str, list[dict]]) -> dict[str, int]: ...
```

- `tables` maps legacy table names (`"ACCT_MASTER"`, `"CONT_MASTER"`, `"ORD_HEADER"`,
  `"ORD_LINE"`) to lists of legacy row dicts (which may still carry `DEL_FLG` and other
  legacy-only keys). Missing table keys mean no rows.
- `load` must: enable `PRAGMA foreign_keys=ON` on `conn`; apply `modern_schema.sql`
  (located next to `migrated.py`); insert only **live** rows (`DEL_FLG` != 'Y'; blank
  means 'N'), dropping legacy-only keys; insert parents before children
  (ACCT_MASTER → CONT_MASTER → ORD_HEADER → ORD_LINE); commit; and return
  `{table: rows_inserted}` for the four tables.
- Dirty data must **fail loudly**: a live row referencing a missing or soft-deleted
  parent must raise `sqlite3.IntegrityError` (never be silently skipped or inserted).

Python ≥ 3.10, stdlib only (`sqlite3` allowed), deterministic, no network.
