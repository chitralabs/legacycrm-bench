# RBC-01 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/role_permissions.csv` under the RBAC semantics in `legacy/SEMANTICS_EXCERPT.md`
(= SYSTEM_OVERVIEW.md §5, §1). No LLM output was used to produce expectations. Derivations:

1. Missing action row: the matrix has no `REP,OPP_MASTER,DELETE` row (REP's OPP_MASTER rows are
   READ/CREATE/UPDATE, all OWN). §5: "a missing (role, object, action) row means NONE" → deny,
   even though the record is owned by the REP user.
2. Unknown role `GUEST` appears in no row of the matrix → every lookup misses → deny by default.
3. `MGR,ACCT_MASTER,READ,ALL` exists. ALL scope has no owner/team condition → allow even when the
   record's OWNER_UID (`U0000009`) and TEAM_CD (`T09`) match nothing about the MGR user.
4. `REP,ACCT_MASTER,READ,TEAM` exists. TEAM scope: user's TEAM_CD (`T01`) equals the record
   owner's TEAM_CD (`T01`) → allow.
5. Same row as (4), record TEAM_CD `T02` ≠ user TEAM_CD `T01` → deny.
6. `REP,OPP_MASTER,UPDATE,OWN` exists. OWN scope: record OWNER_UID `U0000003` equals user's
   USR_ID `U0000003` → allow.
7. Same row as (6), record OWNER_UID `U0000002` ≠ `U0000003` → deny. Team membership is
   irrelevant to OWN scope (§5 defines OWN purely on OWNER_UID).
8. NONE scope: §5 scope set is {ALL, TEAM, OWN, NONE} and a missing row *means* NONE, so an
   explicit NONE row denies. Hand-crafted matrix row `TEMP,ACCT_MASTER,READ,NONE` → deny even
   for the record's owner.
9. Action specificity: `REP,CASE_MASTER,READ,TEAM` exists (allow for a same-team record) but no
   `REP,CASE_MASTER,UPDATE` row exists → UPDATE denied on the very same record (deny-by-default
   is per (role, object, action) triple).
10. SUPP rows in the matrix are CASE_MASTER READ/CREATE/UPDATE and CONT_MASTER/ACCT_MASTER READ;
    no EXPORT row for any object → SUPP EXPORT CASE_MASTER denies.
11. Empty matrix: no row can match any (role, object, action) → all five actions deny
    (deny-by-default under the most hostile fixture).
12. Return type: §5 describes a permission *decision*; the target spec fixes the interface to a
    strict bool. Checked with `is True` / `is False` on one allowed and one denied call.
13. Security/scan expectation: deliverable must not import network/subprocess modules (case
    metadata `security_expectations`; same check as the VAL-01 exemplar).

Note: tests 1–11 exercise only non-ADMIN roles and non-DELETE actions except (1), whose denial
comes from the missing row, not the DELETE DEL_FLG rule — that rule (and ADMIN semantics) is the
distinct behavior slice of RBC-02.

14. (added 2026-09-01 after mutation triage) ADMIN scope bypass: `ADMIN,ACCT_MASTER,READ,ALL`
    exists in the matrix; §5 "The ADMIN role bypasses scope ... its scope is ignored and
    treated as ALL" → allow on a record with foreign owner `U0000009` and foreign team
    `T09`. Closes the gap that no RBC-01 test used an ADMIN user (surviving mutant:
    RBC-01 migrated.py node 80, ADMIN override scope 'ALL' -> 'ALL_X').
15. (added 2026-09-01 after mutation triage) ADMIN DELETE on a live foreign record:
    `ADMIN,OPP_MASTER,DELETE,ALL` exists; the record has `DEL_FLG='N'` so the §5 row-level
    DELETE rule ("record must be soft-deletable, DEL_FLG currently 'N'") holds; scope is
    bypassed for ADMIN → allow (same mutant as (14), DELETE arm).
16. (added 2026-09-01 after mutation triage) Blank DEL_FLG on DELETE: §1 "Booleans stored as
    CHAR(1) in {Y,N}; blank means N" → a blank DEL_FLG is currently 'N', hence deletable.
    `MGR,OPP_MASTER,DELETE,TEAM` exists and user team `T01` equals record team `T01` →
    allow. Closes the gap that every prior test record set DEL_FLG='N' explicitly
    (surviving mutant: RBC-01 migrated.py node 135, blank-DEL_FLG default 'N' -> 'N_X').
