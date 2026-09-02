# SCR-02 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/credit_hold_sweep.crms` under the CRMScript semantics in
`legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §4; conventions §1).
No LLM output was used to produce expectations. All scenarios use CRED_LIMIT 1000.00
unless stated; 80% of limit = 1000 · 8 / 10 = 800.00. Derivations:

1. Hold on: invoiced orders 700 + 500 → exposure 1200 > 1000, CRED_HOLD 'N' → set 'Y',
   audit ("CRED_HOLD_ON","A00000001").
2. Boundary — exposure exactly at the limit: exposure 1000 is not > 1000 → no hold-on;
   with CRED_HOLD 'N', the release IF requires CRED_HOLD='Y' → nothing happens.
3. Hysteresis, held: exposure 900 (800 < 900 ≤ 1000), CRED_HOLD 'Y': hold-on IF fails
   (900 ≤ 1000), release IF fails (900 > 800) → stays 'Y', no audit.
4. Hysteresis, clear: exposure 900, CRED_HOLD 'N': neither IF fires → stays 'N'.
5. Boundary — exposure exactly 80%: 800 ≤ 800 and CRED_HOLD 'Y' → release to 'N',
   audit ("CRED_HOLD_OFF", id). Uses exact decimal math: limit 1000 → threshold 800.00.
6. Clear release: exposure 100 ≤ 800, held → 'N' + CRED_HOLD_OFF.
7. Status filter: orders I:300, S:2000, E:900 → exposure counts only 300 (script's
   `IF ord.STAT_CD = 'I'`); 300 ≤ 1000 → no change. If S/E were counted (3200 > 1000)
   a wrong migration would hold.
8. Soft-deleted order excluded: I:2000 with DEL_FLG 'Y' plus live I:300 → exposure 300 →
   no hold (FOR EACH iterates live rows only).
9. Non-customer account (ACCT_TYP 'P') with exposure 5000 > limit 0: outside the loop's
   `WHERE ACCT_TYP = 'C'` → unchanged, no audit. Same for a soft-deleted 'C' account.
10. Blank CRED_LIMIT: NVL(CRED_LIMIT,0)=0; exposure 0.01 > 0 → hold on. Sequential-IF
    check: after setting 'Y', the release IF needs exposure ≤ 0·8/10 = 0 → 0.01 > 0 →
    does not immediately release.
11. Zero-limit release edge (sequential IFs): CRED_HOLD 'Y', limit 0, exposure 0:
    hold-on IF fails (0 > 0 FALSE); release IF: 0 ≤ 0 AND held → releases to 'N' +
    CRED_HOLD_OFF.
12. Blank CRED_HOLD counts as not held ('' <> 'Y' TRUE): exposure 1200 → set 'Y' +
    CRED_HOLD_ON.
13. Processing order: FOR EACH iterates by primary key ascending (§4), so with input
    accounts [A00000009, A00000002] both crossing their limits, audits come out
    [("CRED_HOLD_ON","A00000002"), ("CRED_HOLD_ON","A00000009")] while the returned list
    keeps input order [A00000009, A00000002].
14. Negative expectation: an account already 'Y' with exposure 1200 > 1000 emits no
    duplicate CRED_HOLD_ON (hold-on IF requires CRED_HOLD <> 'Y').
15. Exposure sums only the account's own orders: another account's invoiced 5000 must not
    leak into A00000001's exposure.
