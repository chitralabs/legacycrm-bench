# Excerpt of SYSTEM_OVERVIEW.md relevant to CFG-02

## 1. Entities and storage (excerpt)

Legacy conventions that migrations must handle:
- **Sentinel values.** Dates stored as `VARCHAR2(8)` in `YYYYMMDD`; the sentinel `00000000`
  means NULL. Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`. Amounts stored as
  `NUMBER(15,2)` in the account's currency; currency code in `CURR_CD` (ISO-4217), blank
  means `USD`.

## 4. CRMScript — rounding convention (excerpt)

`ZPAD(num, w)` (round half-up to integer, right-align, zero-pad to width w) — half-up
rounding is the documented legacy rounding convention for integer conversions.
