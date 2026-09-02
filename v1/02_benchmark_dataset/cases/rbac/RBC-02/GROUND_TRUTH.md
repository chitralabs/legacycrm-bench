# RBC-02 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/role_permissions.csv` under the RBAC semantics in `legacy/SEMANTICS_EXCERPT.md`
(= SYSTEM_OVERVIEW.md §5, §1). No LLM output was used to produce expectations. Derivations:

1. `ADMIN,OPP_MASTER,DELETE,ALL` exists in the matrix. §5: "The ADMIN role bypasses scope" →
   foreign owner (`U0000009`) and team (`T09`) are irrelevant; record `DEL_FLG='N'` satisfies the
   DELETE row-level rule → allow.
2. §5: for ADMIN "its scope is ignored and treated as ALL". A hand-crafted ADMIN row with scope
   `OWN` therefore still grants on a record owned by someone else → allow.
3. The matrix contains no `ADMIN,OPP_MASTER,EXPORT` row (ADMIN's OPP_MASTER rows are
   READ/CREATE/UPDATE/DELETE). §5: "an ADMIN row must still exist for the object/action" →
   deny. A migration that grants here silently widens ADMIN privilege — the central negative
   security expectation of this case.
4. ADMIN's ORD_HEADER rows are READ and UPDATE only → `ADMIN DELETE ORD_HEADER` has no row →
   deny (same §5 clause as (3)).
5. There is no ADMIN row for ORD_LINE at all → `ADMIN READ ORD_LINE` denies (deny-by-default
   applies to ADMIN like any role).
6. `ADMIN,ACCT_MASTER,DELETE,ALL` exists, but the record has `DEL_FLG='Y'`. §5 row-level rule:
   "DELETE additionally requires the record to be soft-deletable (DEL_FLG currently 'N')" →
   deny even for ADMIN (the rule is a row-level conjunct, not a scope, so the ADMIN scope
   bypass does not lift it).
7. Same row and record with `DEL_FLG='N'` → both conjuncts hold → allow.
8. Blank `DEL_FLG`: §1 "Booleans stored as CHAR(1) in {Y,N}; blank means N" → a blank DEL_FLG
   record is currently 'N', hence deletable → `ADMIN,CONT_MASTER,DELETE,ALL` allows.
9. `MGR,OPP_MASTER,DELETE,TEAM` exists. Same-team record (`T01`): scope holds; with
   `DEL_FLG='Y'` the row-level rule denies; with `DEL_FLG='N'` it allows. Shows the DELETE rule
   is independent of the ADMIN override.
10. Same MGR row against a `T09` record with `DEL_FLG='N'`: the TEAM scope fails → deny. A live
    DEL_FLG never *grants* anything; it is only an additional requirement.
11. `ADMIN,ACCT_MASTER,UPDATE,ALL` on a `DEL_FLG='Y'` record → allow: §5 states the row-level
    rule for DELETE only, and the target spec fixes that non-DELETE permission decisions ignore
    DEL_FLG (visibility filtering is a query concern).
12. Enumerating the matrix: ACCT_MASTER has all five ADMIN rows (READ/CREATE/UPDATE/DELETE/
    EXPORT) → all five allowed on a live record; CASE_MASTER has ADMIN rows only for
    READ/UPDATE/DELETE → CREATE and EXPORT deny.
13. Security/scan expectation: deliverable must not import network/subprocess modules
    (case metadata `security_expectations`; same check as the VAL-01 exemplar).

14. (added 2026-09-01 after mutation triage) Granting OWN scope: `REP,OPP_MASTER,UPDATE,OWN`
    exists in the matrix; §5 "OWN scope: OWNER_UID must equal the user id" → user
    `U0000003` on a record with `OWNER_UID='U0000003'` (live, `DEL_FLG='N'`) is allowed.
    Closes the gap that RBC-02's tests exercised ADMIN/DELETE semantics but never a
    granting OWN row (surviving mutant: RBC-02 migrated.py node 186,
    `scope == 'OWN'` -> `'OWN_X'`, which sends OWN grants to the unknown-scope deny).
