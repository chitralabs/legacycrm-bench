# Excerpts from SYSTEM_OVERVIEW.md (Meridian CRM 4.2, authoritative semantics)

## 1. Entities and storage (conventions, excerpt)

- **Soft delete.** `DEL_FLG='Y'` rows are logically deleted; all reads must exclude them
  unless stated. Booleans stored as `CHAR(1)` in {`Y`,`N`}; blank means `N`.
- **Composite keys.** ORD_LINE key is (ORD_ID, LINE_NO); LINE_NO starts at 1, increments
  by 1, and **gaps are forbidden after renumbering**.

Column semantics: LINE_NO is `NUMBER(4)` — a numeric column; string representations of
line numbers compare numerically (2 before 10), never lexicographically.
