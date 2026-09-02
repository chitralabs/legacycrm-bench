# RIN-03 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/legacy_schema_excerpt.sql`, the behavior of `legacy/integrity_check.crms`, and the
conventions in `legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §1/§2); the concrete
modern DDL contract (table set, NOT NULLs, explicit delete actions, retired DEL_FLG,
loader interface) is fixed by target_spec.md. No LLM output was used to produce
expectations. Derivations:

1. Table set: the four legacy tables in scope (target_spec) must exist after
   `executescript` — checked via sqlite_master.
2. Orphan inserts rejected: the legacy system had NO declarative FKs and relied on the
   nightly check to find orphans; the modernization declares the same references
   (CONT_MASTER.ACCT_ID and ORD_HEADER.ACCT_ID → ACCT_MASTER; ORD_LINE.ORD_ID →
   ORD_HEADER, exactly the three lookups integrity_check.crms performs). With
   `PRAGMA foreign_keys=ON`, SQLite raises IntegrityError for a child row whose parent
   key is absent — tests 2–4 insert children with parent ids that were never inserted.
3. RESTRICT on account FKs: integrity_check.crms treats dangling contacts/orders as
   errors to surface (CALL AUDIT('ORPHAN_CONT'/'ORPHAN_OPP')) — the legacy system never
   removes an account's dependents implicitly, so deleting an account that still has
   orders or contacts must fail (tests 5–6).
4. CASCADE on ORD_LINE: integrity_check.crms soft-deletes lines whose header is gone
   (UPDATE line SET DEL_FLG='Y' ... 'ORPHAN_LINE_DEL') — removal of a header removes its
   lines; declared as ON DELETE CASCADE, so deleting header D00000001 leaves 0 rows in
   ORD_LINE (test 7).
5. Declared-action check (security): `PRAGMA foreign_key_list` row format is
   (id, seq, table, from, to, on_update, on_delete, match); the tests assert
   (table, from, to, on_delete) tuples ("ACCT_MASTER","ACCT_ID","ACCT_ID","RESTRICT")
   on both children and ("ORD_HEADER","ORD_ID","ORD_ID","CASCADE") on ORD_LINE. SQLite
   reports the literal declared action, so an implicit default ("NO ACTION") or a
   widened CASCADE on the account FKs fails this test.
6. PK enforcement: ACCT_ID is the legacy PK; ORD_LINE's composite key is
   (ORD_ID, LINE_NO) (§1). Duplicate inserts of either must raise IntegrityError.
7. DEL_FLG retirement: target_spec forbids any DEL_FLG column; regex \bDEL_FLG\b over
   the delivered DDL must not match (negative/security expectation).
8. Clean-load counts: the fixture has 2 live accounts, 1 contact (→ live A00000001),
   1 order (→ live A00000002), 1 line (→ D00000001); all parents precede children, so
   load returns {ACCT_MASTER: 2, CONT_MASTER: 1, ORD_HEADER: 1, ORD_LINE: 1} and the
   order row is queryable with its ACCT_ID intact.
9. Soft-deleted exclusion: §1 — DEL_FLG='Y' rows are logically deleted; the loader
   inserts live rows only, so account A00000009 (DEL_FLG='Y') is absent and the count
   stays 2.
10. Orphan load fails loudly: soft-deleting parent A00000001 means the contact's
    LOOKUP would return '' in the legacy system (§2: no live row) — the modern loader
    must not insert the child; since the parent row is skipped, the child INSERT
    violates the FK and sqlite3.IntegrityError propagates (test asserts raises, i.e.
    no silent skip).
11. Pragma: SQLite keeps foreign-key enforcement per connection; load must leave
    `PRAGMA foreign_keys` = 1 so later writes stay protected.
