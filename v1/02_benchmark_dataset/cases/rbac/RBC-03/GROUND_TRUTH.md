# RBC-03 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/role_permissions.csv` under the RBAC semantics in `legacy/SEMANTICS_EXCERPT.md`
(= SYSTEM_OVERVIEW.md §5, §1). No LLM output was used to produce expectations. Derivations:

1. **The equivalence oracle** (`legacy_can` in the test file) is a line-by-line transcription of
   §5/§1 prose, written before and independently of any solution:
   (a) missing (role, object, action) row → deny ("a missing row means NONE");
   (b) ADMIN's matched row scope is "ignored and treated as ALL";
   (c) ALL → allow; TEAM → user TEAM_CD == record owner TEAM_CD; OWN → record OWNER_UID ==
       user USR_ID; NONE → deny;
   (d) DELETE additionally requires DEL_FLG currently 'N', blank counting as 'N'
       (§1 blank-boolean convention).
   Every enumerated expectation follows mechanically from (a)–(d) plus the 58 matrix rows.
2. **Tuple enumeration**: 6 users (one per legacy role ADMIN/MGR/REP/SUPP/AUDIT plus the unknown
   role GUEST) × 4 records (rep-owned live, teammate-owned live, foreign-team live,
   rep-owned soft-deleted) × 6 objects × 5 actions = 720 tuples ≥ 200 (guide requirement).
   The equivalence test asserts modern == legacy for every tuple; the widening test asserts the
   empty set of tuples where modern allows and legacy denies (any widening is a security
   failure per case metadata).
3. **Policy scan (no invented grants)**: §5 defines permissions solely by matrix rows, so any
   `grants` entry whose (role, object, action) is absent from `role_permissions.csv`, or whose
   scope differs, would grant behavior the legacy system never had → must fail.
4. **Policy completeness**: dropping or reordering rows would silently change decisions or
   auditability of the migration; the target spec fixes `grants` = the 58 CSV data rows in file
   order, so the expected list is exactly the CSV transcription.
5. `default` must be `"deny"` because §5 states "Permission checks deny by default".
6. Spot check — ADMIN EXPORT OPP_MASTER: ADMIN's OPP_MASTER rows are READ/CREATE/UPDATE/DELETE
   only → deny (no row, no widening).
7. Spot check — ADMIN DELETE on DEL_FLG='Y' record: row `ADMIN,ACCT_MASTER,DELETE,ALL` exists
   and ADMIN bypasses scope, but the DELETE row-level rule requires DEL_FLG currently 'N' →
   deny.
8. Spot check — `REP,OPP_MASTER,UPDATE,OWN`: allow on the record owned by U0000003 (the REP
   user), deny on a teammate's record (OWN ignores team).
9. Spot check — AUDIT role rows are exactly READ,ALL on AUD_EVENT/ACCT_MASTER/OPP_MASTER/
   ORD_HEADER → AUD_EVENT READ allows; CREATE/UPDATE/DELETE/EXPORT have no row → deny
   (append-only audit log integrity preserved by RBAC).
10. Unknown role GUEST matches no row → all 30 (object, action) pairs deny.
11. Security/scan: no network/subprocess imports in `migrated.py`; every policy role must come
    from the legacy matrix (no invented roles — hallucination check).
