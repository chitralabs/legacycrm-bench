# Excerpt of SYSTEM_OVERVIEW.md relevant to SCH-03

## 1. Entities and storage (excerpt)

Legacy conventions that migrations must handle:
- **Sentinel values.** Dates stored as `VARCHAR2(8)` in `YYYYMMDD`; the sentinel `00000000` means NULL.
  Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`. Amounts stored as `NUMBER(15,2)` in the
  account's currency; currency code in `CURR_CD` (ISO-4217), blank means `USD`.
- **Status codes.** Single-letter codes with meanings fixed in `data_dictionary.csv`
  (e.g., OPP_MASTER.STAT_CD: P=Prospecting, Q=Qualified, N=Negotiation, W=Closed-Won, L=Closed-Lost).
- **Soft delete.** `DEL_FLG='Y'` rows are logically deleted; all reads must exclude them unless stated.

The schema comment on OPP_MASTER.STAGE_PCT records that it is a *legacy duplicate* of STAT_CD
with the canonical values 10/25/60/100/0 (also encoded in the data-dictionary meaning string
for STAT_CD: Prospecting(10%), Qualified(25%), Negotiation(60%), Closed-Won(100%),
Closed-Lost(0%)).

## 4. CRMScript — rounding convention (excerpt)

`ZPAD(num, w)` (round half-up to integer, right-align, zero-pad to width w) — half-up rounding
is the documented legacy rounding convention for integer conversions.
