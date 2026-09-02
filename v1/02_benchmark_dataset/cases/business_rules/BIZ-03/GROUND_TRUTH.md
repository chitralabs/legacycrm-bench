# BIZ-03 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from rule ORD-003
(`legacy/order_rules.vrl`), the `order_fulfilment` workflow (`legacy/order_fulfilment.xml`),
and the recompute script (`legacy/order_totals.crms`) under the semantics in
`legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §1/§2/§3/§4). The invoiced-totals
freeze is the modernization decision stated in target_spec.md (the legacy nightly script
recomputed I orders too; the modern contract freezes them — "the amount invoiced is the
amount owed"). No LLM output was used to produce expectations. Derivations:

1. I→X cancel: workflow transition `from="I" to="X" event="cancel"` with actions in
   document order `<audit code="ORD_CANC_INV"/>` then `<notify template="credit_note"/>`
   → new STAT_CD 'X', audits ["ORD_CANC_INV"], notifies ["credit_note"]. (Tests 1–3;
   a migration that kept only ORD-003 and dropped the workflow actions fails 2–3.)
2. I→I: ORD-003 passes (`STAT_CD <> 'I'` is false) and no workflow transition fires
   (state unchanged) → vacuous: unchanged copy, no audits/notifies.
3. I→A / I→E / I→S: ORD-003's negated conjunction is violated (OLD='I', new ≠ 'I',
   new ≠ 'X') → rule fails → E5003 with the literal message "Invoiced order can only
   be cancelled". (Tests 5–8; a migration that kept only the workflow — where a
   non-matching event would be a WF_NOMATCH no-op — fails these, closing the
   cross-check the case exists for.)
4. Non-invoiced input to transition_invoiced is outside the function's contract →
   ValueError per target_spec (not a business violation).
5. Frozen invoiced totals (target_spec modernization): STAT_CD='I' → order and lines
   returned unchanged, audits [] — even though the line says 5 × 10.01, TOT_AMT stays
   the stored "100.00" and stale EXT_AMT "10.01" is preserved (tests 10–11, negative).
6. Cancelled orders: order_totals.crms iterates `WHERE ... STAT_CD <> 'X'`, so an X
   order is never recomputed → unchanged, no audit.
7. Entered-order recompute: EXT_AMT = NVL(1,0) × NVL(10.01,0) = 10.01;
   total = 10.01; TOT_AMT = 10.01 × (100 − 50)/100 = 5.005 → **half-up to cents**
   (script header comment; ZPAD-style half-up per §4) → 5.01. Stored TOT_AMT "0"
   differs → audit ["ORD_RETOTAL"]. (Float arithmetic gives 10.01*50/100 =
   5.005000000000001 → but naive round() half-even on 5.005 float can yield 5.0 or
   5.01 depending on representation; the decimal derivation 5.005 → 5.01 is the
   documented one.)
8. No-change case: 2 × 10.00 = 20.00, discount 0 → 20.00 equals stored "20.00" →
   the script's `IF ord.TOT_AMT <> discounted` guard is false → no ORD_RETOTAL
   (negative expectation).
9. Soft-deleted line: §1 — DEL_FLG='Y' excluded from reads; the 100 × 99.00 deleted
   line contributes nothing → TOT_AMT = 2 × 10.00 = 20.00.
10. Blank coercions: §1 — empty string coerces to 0 and NVL(QTY,0)/NVL(DISC_PCT,0)
    default to 0 → EXT_AMT 0.0, TOT_AMT 0.0.
11. Purity is a target_spec requirement (rule 5): both functions leave inputs equal to
    their pre-call snapshots.
