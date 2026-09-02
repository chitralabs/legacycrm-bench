# RIN-01 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from the first
FOR EACH loop of `legacy/integrity_check.crms` under the semantics in
`legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §1/§2/§4). No LLM output was used to
produce expectations. Derivations:

1. Live contact + live matching account: LOOKUP(ACCT_MASTER, ACCT_ID, 'A00000001',
   ACCT_ID) returns 'A00000001' ≠ '' → not an orphan → `[]`.
2. Missing account id A00000099: no row at all → LOOKUP returns '' → orphan
   → `["K00000001"]`.
3. Soft-deleted account: §2 — LOOKUP "returns matching column value or empty string if
   no **live** row". The only A00000001 row has DEL_FLG='Y', so LOOKUP returns '' and
   the contact IS an orphan. This is the case's key expectation.
4. Soft-deleted contact: the script's loop is `FOR EACH cont IN CONT_MASTER WHERE
   DEL_FLG = 'N'` and §4 says FOR EACH iterates live rows — a soft-deleted contact is
   never examined, hence never reported, even with a dangling ACCT_ID → `[]`
   (negative expectation).
5. Blank DEL_FLG: §1 — blank CHAR(1) boolean means 'N', so an account with DEL_FLG=''
   is live and its contact is not an orphan.
6. Blank ACCT_ID: LOOKUP with key '' matches no live account row (ACCT_ID is a
   non-blank primary key) → returns '' → orphan.
7. Ordering: §4 — FOR EACH iterates live rows "ordered by primary key ascending";
   CONT_MASTER's primary key is CONT_ID, so orphans are reported in ascending CONT_ID
   order regardless of input order: K00000005/K00000002/K00000009 in the input yield
   [K00000002, K00000005, K00000009].
8. Mixed population: applying rules 1–4 row by row — K00000004→live ref (ok),
   K00000001→soft-deleted acct (orphan), K00000003→missing acct (orphan),
   K00000002→live ref (ok), K00000005→soft-deleted contact (skipped); PK ordering of
   the two orphans gives [K00000001, K00000003].
9. Empty contacts → nothing to examine → []. No accounts at all → every live contact's
   LOOKUP misses → both reported, PK order [K00000001, K00000002].
10. Purity: the legacy check only CALLs AUDIT and counts; it never updates CONT_MASTER
    or ACCT_MASTER in this pass, so the migration must not mutate inputs.
