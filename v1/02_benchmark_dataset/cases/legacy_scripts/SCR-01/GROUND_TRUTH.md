# SCR-01 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/order_totals.crms` under the CRMScript semantics in `legacy/SEMANTICS_EXCERPT.md`
(= SYSTEM_OVERVIEW.md §4; conventions §1). The script comment fixes rounding: "rounding
half-up to cents". No LLM output was used to produce expectations. Derivations:

1. Two live lines, QTY 3 × UNIT_PRC 19.99 and QTY 2 × UNIT_PRC 5.25:
   EXT_AMT = 3·19.99 = 59.97 and 2·5.25 = 10.50 (exact cents, no rounding needed).
   total = 59.97 + 10.50 = 70.47. DISC_PCT 0 → TOT_AMT = 70.47·100/100 = 70.47.
   Incoming TOT_AMT "0" ≠ 70.47 → one audit ("ORD_RETOTAL","O00000001").
2. Discount rounding: single line 3 × 19.99 = 59.97; DISC_PCT 15 →
   59.97·(100−15)/100 = 59.97·0.85 = 50.9745 → half-up to cents = **50.97**
   (third decimal 4 rounds down).
3. Half-up boundary: single line 1 × 10.01 = 10.01; DISC_PCT 50 →
   10.01·50/100 = 5.005 → half-up = **5.01**. Distinguishes half-up from
   round-half-even (5.00) and from naive binary-float rounding
   (Python float 5.005 is 5.00499999…, so float round() gives 5.00 — wrong).
4. No-audit case: line 2 × 5.25 = 10.50, DISC 0, incoming TOT_AMT "10.5":
   numerically 10.5 = 10.50 → `ord.TOT_AMT <> discounted` FALSE → no audit,
   even though the line's stale EXT_AMT "999" is corrected to 10.50.
5. Soft-deleted line: live line 1 × 10.00 plus DEL_FLG='Y' line (5 × 100, stale
   EXT_AMT "500"): the loop `WHERE DEL_FLG = 'N'` skips it → total = 10.00 only;
   the deleted line is returned with EXT_AMT still "500" (untouched).
6. Cancelled order (STAT_CD 'X') and soft-deleted order (DEL_FLG 'Y') are outside the
   outer loop's WHERE → returned unchanged, audits [].
7. Empty QTY coerces to 0 (NVL/empty-string rule) → EXT_AMT 0.0; blank DISC_PCT
   coerces to 0 → TOT_AMT = total.
8. Line order and count are preserved (the script updates rows in place; the modern copy
   must not reorder or drop rows).
9. Inputs are not mutated (modern copies; the legacy UPDATE-in-place is represented by the
   returned rows).
10. Negative expectation: recomputation emits no audit codes other than ORD_RETOTAL, and
    none at all when the total is unchanged (case 4).
