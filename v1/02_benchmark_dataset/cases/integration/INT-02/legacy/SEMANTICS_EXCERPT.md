# Excerpts from SYSTEM_OVERVIEW.md (Meridian CRM 4.2, authoritative semantics)

## 1. Entities and storage (conventions, excerpt)

Legacy conventions that migrations must handle:
- **Sentinel values.** Dates stored as `VARCHAR2(8)` in `YYYYMMDD`; the sentinel `00000000` means NULL.
  Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`. Amounts stored as `NUMBER(15,2)` in the
  account's currency; currency code in `CURR_CD` (ISO-4217), blank means `USD`.

## 4. CRMScript — semantics (builtins, excerpt)

Expressions use VRL operators/functions plus string concatenation `&` and the additional builtins
`FIXED(s, w)` (left-align, space-pad, truncate to width w), `ZPAD(num, w)` (round half-up to integer,
right-align, zero-pad to width w), `CHR(n)` (character from code point). `NVL(x, default)` returns
`default` when `x` is empty/missing.

## 6. Integrations — semantics (excerpt)

Fixed-width payload layouts are in `data_dictionary.csv` rows with DICT_TYPE=LAYOUT
(this case: `export_acct_layout.csv`, the EXPORT_ACCT rows; POSITION is 1-based).
