# Excerpt of legacy_system/SYSTEM_OVERVIEW.md (authoritative semantics)

## 8. Audit log — semantics

AUD_EVENT columns: EVT_ID, EVT_TS (YYYYMMDDHH24MISS string), EVT_CD, USR_ID, ENT_NAME, ENT_ID,
OLD_VAL, NEW_VAL. Every UPDATE to an audited column (audit_config.cfg lists them) writes one row
per changed column, with OLD_VAL/NEW_VAL as strings. Audit rows are append-only; migrations must
preserve append-only behavior and per-column granularity unless the case's target spec says otherwise.

## 1. Entities and storage (relevant conventions)

- Dates stored as `VARCHAR2(8)` in `YYYYMMDD`; timestamps in AUD_EVENT as `VARCHAR2(14)`
  `YYYYMMDDHH24MISS` (year, month, day, hour-of-24, minute, second).
- AUD_EVENT.EVT_ID is the numeric primary key; it is assigned in strictly increasing order of
  event occurrence, so ascending EVT_ID is the canonical event order.
