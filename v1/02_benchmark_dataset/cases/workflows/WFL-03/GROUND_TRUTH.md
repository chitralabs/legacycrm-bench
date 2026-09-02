# WFL-03 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/order_fulfilment.xml` under the workflow-engine semantics in
`legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §3; LOOKUP and coercions per §2;
soft-delete convention per §1). No LLM output was used to produce expectations.

1. `fire("E","approve",{TOT_AMT:"250.00"})`: guard NVL(TOT_AMT,0)>0 → 250>0 TRUE → A,
   audits ["ORD_APPR"], notifies [], matched True.
2. `TOT_AMT:"0"` → 0>0 FALSE → no other from=E/approve row → no-op: state E,
   audits ["WF_NOMATCH"], matched False.
3. `TOT_AMT:""` coerces to 0 (§2 empty string in numeric comparison) → same no-op as (2).
4. `fire("A","ship",...)` → S, audits ["ORD_SHIP"], notifies ["shipped"].
5. `fire("S","invoice",...)` → I, audits ["ORD_INV"], notifies [].
6. `fire("E","cancel",...)`: E→X row is unguarded → X, audits ["ORD_CANC"].
7. `fire("A","cancel", rec, tables)` with a live ACCT_MASTER row {ACCT_ID matching,
   CRED_HOLD:"N"}: LOOKUP returns "N"; "N" <> "Y" TRUE → X, audits ["ORD_CANC"],
   notifies [].
8. Same with CRED_HOLD:"Y" on the live row: LOOKUP returns "Y"; "Y" <> "Y" FALSE → guard
   blocks; no other row has from=A and event=cancel (E→X and I→X differ in `from`) → no-op:
   state stays A, audits ["WF_NOMATCH"], matched False. The blocked cancel must emit
   neither ORD_CANC nor credit_note (negative expectation).
9. Account absent from ACCT_MASTER: LOOKUP returns "" (no live row); "" <> "Y" TRUE →
   cancel allowed → X, ["ORD_CANC"].
10. Account row present with CRED_HOLD:"Y" but DEL_FLG:"Y": LOOKUP sees live rows only
    (§2: "empty string if no live row") → returns "" → cancel allowed. This is the
    soft-delete trap: a naive lookup that ignores DEL_FLG would wrongly block.
11. `fire("I","cancel",...)`: only the I→X row matches (from=I) → X, audits
    ["ORD_CANC_INV"], notifies ["credit_note"]. Priority check: ORD_CANC must NOT appear —
    an implementation matching on event alone would wrongly pick the earlier E→X row
    (document order) and emit ORD_CANC.
12. `fire("S","cancel",...)`: no transition has from=S and event=cancel → WF_NOMATCH
    (shipped orders cannot be cancelled).
13. `fire("X","cancel",...)`: X is terminal → WF_NOMATCH.
14. LOOKUP uses the record's ACCT_ID as the key value: with two live accounts A1
    (CRED_HOLD Y) and A2 (CRED_HOLD N), an order whose ACCT_ID is "A2" cancels fine and an
    order on "A1" is blocked — the guard must not match some other row.
15. Input record and tables must not be mutated (record copy per §3 contract).

16. (added 2026-09-01 after mutation triage) Matched-fire return shape: the target spec
    requires the result dict to have exactly the keys `state`, `record`, `audits`,
    `notifies`, `matched` on every fire. On the matched E→A approve (guard
    `NVL(TOT_AMT,0) > 0` TRUE for TOT_AMT='250.00'), the transition's actions are a
    single `<audit code="ORD_APPR"/>` with no `<set>`, so the returned `record` equals
    the input order dict. Closes the gap that no test read `res["record"]` (or the key
    set) on a matched fire (surviving mutant: WFL-03 migrated.py node 300, return key
    'record' -> 'record_X').
