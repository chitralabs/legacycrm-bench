# CFG-03 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** by reading
`legacy/workflows.xml` element by element, under the workflow semantics in
`legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §3, which makes document order and
verbatim guards load-bearing). No LLM output was used. Derivations:

1. Workflow count and order: the XML declares, in order, `opportunity_pipeline`
   (entity OPP_MASTER), `case_lifecycle` (CASE_MASTER), `order_fulfilment` (ORD_HEADER);
   all three use state_field STAT_CD.
2. States, in XML order: opportunity_pipeline P,Q,N,W,L; case_lifecycle N,A,P,R,X;
   order_fulfilment E,A,S,I,X — five each.
3. Initial states: exactly one `initial="true"` per workflow — P (opportunity_pipeline),
   N (case_lifecycle), E (order_fulfilment); every other state is non-initial.
4. Timers: only case_lifecycle has them — state N: after_days=2 event auto_escalate;
   state A: after_days=7 event auto_escalate. All other states of all workflows: none.
5. Transition counts, counted by hand: opportunity_pipeline 6 (P→Q qualify, Q→N advance,
   N→W close_won, P→L close_lost, Q→L close_lost, N→L close_lost); case_lifecycle 8
   (N→A assign, N→A auto_escalate, A→A auto_escalate, A→P await_customer, P→A
   customer_reply, A→R resolve, R→X close, R→A reopen); order_fulfilment 6 (E→A approve,
   A→S ship, S→I invoice, E→X cancel, A→X cancel, I→X cancel). Total 20.
6. Guards, decoded verbatim from the XML entities (`&gt;` → `>`, `&lt;&gt;` → `<>`):
   P→Q qualify: `NVL(AMT,0) > 0`; N→W close_won: `CLOSE_DT <> '00000000'`; the three
   close_lost transitions: `LOST_RSN <> ''`; N→A assign: `OWNER_UID <> ''`; A→A
   auto_escalate: `ESC_FLG <> 'Y'`; A→R resolve: `RES_DT <> '00000000'`; E→A approve:
   `NVL(TOT_AMT,0) > 0`; A→X cancel: `LOOKUP(ACCT_MASTER, ACCT_ID, ACCT_ID, CRED_HOLD) <> 'Y'`.
   All other transitions have no `<guard>` → `null`.
7. Actions, in XML order, e.g.: P→Q qualify → [set STAGE_PCT "25", audit OPP_QUAL]; N→W
   close_won → [set STAGE_PCT "100", audit OPP_WON, notify won_deal]; N→A auto_escalate →
   [set ESC_FLG "Y", set SEV_CD "=NVL(SEV_CD,'3')" (the `=EXPR` form kept verbatim), audit
   CASE_ESC, notify escalation]; R→A reopen → [set RES_DT "00000000", audit CASE_REOPEN];
   I→X cancel → [audit ORD_CANC_INV, notify credit_note]. P→A customer_reply has no
   `<actions>` → [].
8. Completeness/hallucination oracle: the set of (workflow, from, to, event) tuples parsed
   from the XML by the test itself (stdlib xml.etree on the case's own legacy artifact)
   must equal the JSON's set in both directions. The hand counts of entry 5 pin the XML
   parse against accidental drift.
