# BIZ-01 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from rule ACC-004
in `legacy/account_rules.vrl`, the release audit in `legacy/credit_hold_sweep.crms`, and
the semantics in `legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §1/§2/§4). No LLM
output was used to produce expectations. Derivations:

1. ACC-004 expr: `NOT (OLD.CRED_HOLD='Y' AND CRED_HOLD='N' AND CRED_LIMIT <= 0)`.
   The service models the release update OLD.CRED_HOLD='Y' → CRED_HOLD='N'. With
   CRED_LIMIT 50000.00 > 0 the conjunction is false → rule passes → release succeeds
   and CRED_HOLD becomes 'N'.
2. Audit on success: credit_hold_sweep.crms performs the same release as
   `UPDATE acct SET CRED_HOLD='N'` + `CALL AUDIT('CRED_HOLD_OFF', acct.ACCT_ID)`, so
   the modern service emits exactly one `{"code": "CRED_HOLD_OFF", "entity_id":
   "A00000001"}` event.
3. Only CRED_HOLD changes: the legacy release updates a single column; all other
   fields of the returned account equal the input.
4. CRED_LIMIT = 0.00: conjunction true (Y→N and 0 <= 0) → rule fails → write rejected
   with the rule's code/message → BusinessRuleViolation code "E1004".
5. Negative CRED_LIMIT (-100.00 <= 0) → same failure.
6. Blank CRED_LIMIT: §2 — empty string in numeric comparison coerces to 0 → 0 <= 0 →
   E1004 (the guard cannot be bypassed by an unset limit).
7. CRED_LIMIT = 0.01 > 0 → conjunction false → release allowed, one audit.
8. Not on hold (CRED_HOLD='N'): OLD.CRED_HOLD is not 'Y', so ACC-004's conjunction is
   false regardless of the limit → no error; and since no Y→N transition occurs, the
   sweep's release branch (`... AND acct.CRED_HOLD = 'Y'`) would not run → no
   CRED_HOLD_OFF audit (negative expectation).
9. Blank CRED_HOLD: §1 — blank CHAR(1) boolean means 'N' → same as (8); the returned
   copy preserves the blank value (nothing to release).
10. Message fidelity: the raised violation carries the rule's literal message
    "Cannot release credit hold with zero credit limit".
11. Purity is a target_spec requirement (rule 4): input equals its pre-call snapshot on
    both the success and the failure path.
