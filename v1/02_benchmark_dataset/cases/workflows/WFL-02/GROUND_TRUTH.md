# WFL-02 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/case_lifecycle.xml` under the workflow-engine semantics in
`legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §3, guard/set expressions per §2).
No LLM output was used to produce expectations. Derivations:

1. `fire("N","assign",{OWNER_UID:"U0000002"})`: guard `OWNER_UID <> ''` TRUE → A,
   audits ["CASE_ASSIGN"], no sets, no notifies, matched True.
2. `OWNER_UID:""` (and missing key, which reads as empty string) → guard FALSE → no other
   from=N/assign transition exists → no-op: state N, audits ["WF_NOMATCH"], matched False.
3. `fire("N","auto_escalate",{SEV_CD:"", ESC_FLG:"N"})`: unguarded N→A row fires. Sets in
   order after state change: ESC_FLG:="Y" (literal), then SEV_CD:==NVL(SEV_CD,'3') — SEV_CD
   is empty → default "3". audits ["CASE_ESC"], notifies ["escalation"].
4. Same with SEV_CD:"1": NVL returns the non-empty value → SEV_CD stays "1" (the
   escalation must not overwrite an explicit severity).
5. `fire("A","auto_escalate",{ESC_FLG:"N"})`: A→A row's guard `ESC_FLG <> 'Y'` TRUE →
   state stays "A" but matched True (self-transition, not a no-op); ESC_FLG:="Y"; audits
   ["CASE_ESC"]; notifies ["escalation"]. This transition has no SEV_CD set action, so
   SEV_CD is left untouched even when blank.
6. `fire("A","auto_escalate",{ESC_FLG:"Y"})`: guard FALSE → no-op WF_NOMATCH (an already
   escalated case is never double-escalated; no second CASE_ESC audit or notify).
7. Blank/missing ESC_FLG is `<> 'Y'` → the A→A row fires (blank means N per §1).
8. `fire("A","await_customer",...)` → P, audits ["CASE_PEND"].
9. `fire("P","customer_reply",...)`: transition has no actions element → A, audits [],
   notifies [], matched True.
10. `fire("A","resolve",{RES_DT:"20260810"})`: guard string-inequality to sentinel TRUE →
    R, audits ["CASE_RES"].
11. `fire("A","resolve",{RES_DT:"00000000"})`: guard FALSE → WF_NOMATCH no-op.
12. `fire("R","close",...)` → X, audits ["CASE_CLOSE"].
13. `fire("R","reopen",{RES_DT:"20260810"})` → A; set RES_DT:="00000000" (literal string)
    applies after the state change → returned record has RES_DT "00000000"; audits
    ["CASE_REOPEN"].
14. Chained consequence of (13)+(11): feeding the reopened record straight into
    `fire("A","resolve",...)` is a no-op because reopen cleared RES_DT to the sentinel —
    the resolve guard now fails. This is the observable point of "sets apply after the
    state change": the cleared value is in the returned record.
15. State X has no outgoing transitions → `fire("X","reopen",...)` → WF_NOMATCH.
16. Negative expectation: the no-op in (6) leaves the record copy unchanged and emits no
    "escalation" notify.
