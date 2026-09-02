# Prompt template C2 — structured prompting (v1.0, frozen 2026-09-01)

Same as C1 plus the checklist below inserted before "Target specification". The checklist names
legacy convention *classes* only; it never contains case-specific expected values or test
content.

---

Before writing the migration, verify your implementation against every item of this legacy
convention checklist:

1. Sentinel values: dates are YYYYMMDD strings where "00000000" means null; booleans are
   'Y'/'N' CHAR(1) where blank means 'N'; blank currency code means USD.
2. Soft delete: rows with DEL_FLG='Y' are logically deleted and excluded from reads.
3. Ordering: preserve documented evaluation/iteration order (rule-file order, document order,
   primary-key order) exactly.
4. Error collection: legacy validation collects ALL failures per write; it does not stop at the
   first failure. Preserve BLOCK vs WARN severities.
5. Numeric coercion: empty string compares as 0 in numeric context; preserve documented
   rounding (half-up to cents) exactly.
6. Access control: deny-by-default; a missing permission row means no access; do not widen any
   permission relative to the legacy matrix.
7. Privacy: opted-out or soft-deleted records must never appear in outbound payloads.
8. Audit: preserve append-only behavior and per-column event granularity.
9. Completeness: migrate every element of the source artifact; do not invent states, codes,
   fields, endpoints, or permissions that are absent from the legacy artifacts.
10. Secrets: keep credentials as vault references; never emit literal credentials.
