# Excerpt of SYSTEM_OVERVIEW.md relevant to CFG-01

## 1. Entities and storage (excerpt)

Column semantics: `data_dictionary.csv`.

Legacy conventions:
- **Status codes.** Single-letter codes with meanings fixed in `data_dictionary.csv`
  (e.g., OPP_MASTER.STAT_CD: P=Prospecting, Q=Qualified, N=Negotiation, W=Closed-Won,
  L=Closed-Lost).
- **Sentinel values.** Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`. Currency
  code in `CURR_CD` (ISO-4217), blank means `USD`. Dates `YYYYMMDD` with `00000000` = null.
  (These are storage conventions, not enumerated code tables.)
- **Soft delete.** `DEL_FLG='Y'` rows are logically deleted (a convention, not a code table).

Data-dictionary COLUMN rows encode code tables as semicolon-separated `code=label` pairs in
the MEANING field, e.g. `"C=Customer;P=Prospect;R=Partner;X=Inactive"`. Some labels carry a
parenthesized operational annotation, e.g. `"P=Prospecting(10%)"` (the STAGE_PCT duplicate)
and `"1=Critical(4h target)"` (the response-time target); the annotation is not part of the
label. Some meanings also carry a default note (`"blank=E"`, `"blank=USD"`) — a storage
default, not an enumerated code.
