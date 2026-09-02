# Excerpt of legacy_system/SYSTEM_OVERVIEW.md (authoritative semantics)

## 8. Audit log — semantics

AUD_EVENT columns: EVT_ID, EVT_TS (YYYYMMDDHH24MISS string), EVT_CD, USR_ID, ENT_NAME, ENT_ID,
OLD_VAL, NEW_VAL. Every UPDATE to an audited column (audit_config.cfg lists them) writes one row
per changed column, with OLD_VAL/NEW_VAL as strings. Audit rows are append-only; migrations must
preserve append-only behavior and per-column granularity unless the case's target spec says otherwise.

## audit_config.cfg format (from the artifact itself)

Line-oriented. `#` starts a comment; blank lines are ignored. Each configuration line is:

```
AUDIT <TABLE> <COLUMN>
```

declaring that `<COLUMN>` of `<TABLE>` is audited. File order of the lines is the canonical
order of audited columns within a table.
