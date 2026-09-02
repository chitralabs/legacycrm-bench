# Excerpt of SYSTEM_OVERVIEW.md relevant to SCH-02

## 1. Entities and storage (excerpt)

Schema: `legacy_schema.sql` (legacy SQL dialect: `VARCHAR2`, `NUMBER`, no FK constraints — referential
integrity is enforced by application code and nightly batch checks). Column semantics: `data_dictionary.csv`.

Legacy conventions that migrations must handle:
- **Sentinel values.** Dates stored as `VARCHAR2(8)` in `YYYYMMDD`; the sentinel `00000000` means NULL.
  Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`. Amounts stored as `NUMBER(15,2)` in the
  account's currency; currency code in `CURR_CD` (ISO-4217), blank means `USD`.
- **Status codes.** Single-letter codes with meanings fixed in `data_dictionary.csv`.
- **Soft delete.** `DEL_FLG='Y'` rows are logically deleted; all reads must exclude them unless stated.
