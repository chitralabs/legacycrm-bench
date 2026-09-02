# WFL-01 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/opportunity_pipeline.xml` under the workflow-engine semantics in
`legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §3, guard expressions per §2).
No LLM output was used to produce expectations. Derivations:

1. `fire("P","qualify",{AMT:"1500.00",...})`: transition P→Q matches (from=P, event=qualify);
   guard `NVL(AMT,0) > 0` → 1500 > 0 TRUE. State becomes Q; `<set STAGE_PCT "25">` applies
   after the state change → record STAGE_PCT == "25" (literal string per spec rule 3);
   audits ["OPP_QUAL"]; no notify; matched True.
2. Same event with AMT="0": guard 0 > 0 FALSE → no transition matches → no-op per §3:
   state stays "P", audits ["WF_NOMATCH"], notifies [], matched False, record unchanged.
3. AMT="" coerces to 0 in numeric comparison (§2) → same no-match outcome as (2).
4. `fire("Q","advance",...)`: Q→N has no guard → fires; only action is set STAGE_PCT "60";
   audits [] (no audit action), notifies [].
5. `fire("N","close_won",{CLOSE_DT:"20261015"})`: guard `CLOSE_DT <> '00000000'` is string
   inequality to the sentinel literal → TRUE. → W, STAGE_PCT "100", audits ["OPP_WON"],
   notifies ["won_deal"].
6. CLOSE_DT="00000000": `'00000000' <> '00000000'` FALSE → guard fails → WF_NOMATCH no-op.
7. `fire("P","close_lost",{LOST_RSN:"CM"})`: P→L guard `LOST_RSN <> ''` TRUE → L,
   STAGE_PCT "0", audits ["OPP_LOST"].
8. `fire("Q","close_lost",{LOST_RSN:""})`: the only from=Q close_lost transition's guard is
   FALSE → no-op (guards must be evaluated per-transition, not skipped).
9. `fire("N","close_lost",{LOST_RSN:"PR"})`: N→L row (third close_lost row in document
   order) fires → L, audits ["OPP_LOST"].
10. `fire("P","close_won",...)`: no transition has from=P and event=close_won → WF_NOMATCH.
11. From terminal state W no transitions exist → any event (e.g. "qualify") → WF_NOMATCH.
12. The input record dict must not be mutated by a successful fire (spec: "record" is a new
    dict; `<set>` applies to the copy). Checked by comparing the input to a snapshot.
13. Negative expectation: a successful qualify emits exactly ["OPP_QUAL"] — no OPP_LOST /
    OPP_WON codes and no notifies leak in from other transitions' action lists.

14. (added 2026-09-01 after mutation triage) Successful Q→L close: the workflow XML's
    `<transition from="Q" to="L" event="close_lost">` has guard `LOST_RSN <> ''`; with
    LOST_RSN='CM' the guard is TRUE, so the transition fires → state 'L', action
    `<set field="STAGE_PCT" value="0"/>` writes "0" onto the record copy, and
    `<audit code="OPP_LOST"/>` emits exactly ["OPP_LOST"]; matched True. Closes the gap
    that this row was only ever exercised with LOST_RSN='' (NOMATCH) (surviving mutants:
    WFL-01 migrated.py node 119, to-state 'L' -> 'L_X', and node 277, set payload
    '0' -> '0_X').
