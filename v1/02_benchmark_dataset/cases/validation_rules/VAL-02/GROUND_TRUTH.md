# VAL-02 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/account_rules.vrl` under the VRL semantics in `legacy/SEMANTICS_EXCERPT.md`
(= SYSTEM_OVERVIEW.md §2). No LLM output was used. Derivations:

1. Compliant insert `{ACCT_NM:'Acme Industrial', ACCT_TYP:'C', ANN_REV:1000, REGION_CD:'NAM'}`:
   ACC-001 pass (LEN=15≥2); ACC-002 pass (C); ACC-003 pass (1000≥0); ACC-004 not applicable
   (UPDATE-only); ACC-005 pass (LEN('NAM')=3) → `[]`.
2. One-char name `ACCT_NM:'A'` → LEN=1 < 2 → ACC-001 fails → E1001, severity BLOCK (default).
3. `ACCT_TYP:'Z'` matches none of C/P/R/X → ACC-002 fails → E1002.
4. `ANN_REV:-1` → NVL(-1,0) = -1 < 0 → ACC-003 fails → E1003.
5. Blank `ANN_REV:''` → NVL('',0) = 0 ≥ 0 → ACC-003 passes (NVL default rule).
6. Credit-hold release with zero limit, UPDATE: old `CRED_HOLD:'Y'`, new `CRED_HOLD:'N'`,
   `CRED_LIMIT:0` → the NOT(...) expr is FALSE → ACC-004 fails → E1004 BLOCK;
   is_blocked True.
7. Same images but `CRED_LIMIT:5000` → 5000 ≤ 0 FALSE → conjunction FALSE → NOT(...) TRUE →
   ACC-004 passes.
8. Same record under INSERT: ACC-004 does not run (WHEN UPDATE only) → no E1004. (Even if it
   ran, OLD.CRED_HOLD would be '' ≠ 'Y'.)
9. Keeping the hold (old 'Y' → new 'Y') with CRED_LIMIT 0: `CRED_HOLD='N'` conjunct FALSE →
   ACC-004 passes.
10. Blank CRED_LIMIT on a release: '' coerces to 0 in numeric context → 0 ≤ 0 TRUE →
    ACC-004 fails → E1004.
11. `REGION_CD:'NA'` → LEN=2 ≠ 3 → ACC-005 fails → E1005 with SEVERITY WARN; a record
    failing only ACC-005 has is_blocked() == False (WARN does not block).
12. Collect-all in file order: `{ACCT_NM:'A', ACCT_TYP:'Z', ...}` (rest compliant) → codes
    exactly [E1001, E1002] in that order.
13. Empty record insert `{}`: ACC-001 LEN('')=0<2 fails (E1001); ACC-002 '' not in {C,P,R,X}
    fails (E1002); ACC-003 NVL('',0)=0≥0 passes; ACC-004 n/a; ACC-005 LEN('')=0≠3 fails
    (E1005 WARN) → codes [E1001, E1002, E1005]; is_blocked True (E1001/E1002 are BLOCK).
14. Messages come verbatim from the rule file, e.g. E1004 → "Cannot release credit hold with
    zero credit limit".

15. (added 2026-09-01 after mutation triage) Remaining legal account types: ACC-002's expr
    is the four-way disjunction `ACCT_TYP = 'C' OR 'P' OR 'R' OR 'X'`, so an otherwise
    compliant insert with ACCT_TYP 'P', 'R', or 'X' passes every rule (ACC-001/003/005
    unchanged from derivation 1; ACC-004 UPDATE-only) → `[]` for each. Closes the gap
    that only 'C' (valid) and 'Z' (invalid) were exercised (surviving mutant: VAL-02
    migrated.py node 233, tuple ('C','P','R','X') -> ('C','P','R_X','X'), which makes
    legal type 'R' raise E1002).
