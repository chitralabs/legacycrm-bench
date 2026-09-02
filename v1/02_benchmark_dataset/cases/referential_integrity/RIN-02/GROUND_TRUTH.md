# RIN-02 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from the ORD_LINE
composite-key convention in `legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §1:
"LINE_NO starts at 1, increments by 1, and gaps are forbidden after renumbering") and the
`legacy/ord_line_schema.sql` column types. Per-order grouping, output ordering, purity,
and idempotence are fixed by target_spec.md. No LLM output was used to produce
expectations. Derivations:

1. Gaps closed: live lines numbered 1,3,7 keep relative order and become 1,2,3 — direct
   application of "starts at 1, increments by 1, gaps forbidden".
2. Field preservation: renumbering touches only LINE_NO; PROD_ID/QTY/UNIT_PRC of the
   line formerly numbered 5 travel with it to its new number.
3. Soft delete: §1 — DEL_FLG='Y' rows are excluded from all reads; a deleted line
   therefore neither appears nor occupies a number: [1, Y-deleted 2, 3] → two live
   lines numbered 1,2 and the deleted line's PROD_ID (P00000099) absent (negative
   expectation).
4. Already-contiguous input maps every line to its own number (1→1, 2→2, 3→3).
5. Idempotence: after one pass the numbering is exactly 1..n per order with no deleted
   rows left, so a second pass changes nothing — `renumber(renumber(x)) == renumber(x)`.
6. Numeric order: LINE_NO is NUMBER(4); "10" > "2" numerically although "10" < "2"
   lexicographically. Input ("10", "2") must surface products in order P00000002 then
   P00000010 with new numbers 1,2.
7. Per-order restart: the key is (ORD_ID, LINE_NO), so numbering is scoped to ORD_ID —
   D00000001's lines 5,9 become 1,2 and D00000002's line 8 becomes 1.
8. Output ordering (target_spec rule 3): by ORD_ID ascending then new LINE_NO →
   [(D00000001,1), (D00000002,1), (D00000002,2)] for the mixed fixture.
9. New LINE_NO values are ints (NUMBER column, modern representation per target_spec
   rule 2); `type(...) is int` also rejects booleans.
10. Purity (target_spec rule 5): input rows compare equal to a pre-call snapshot.
11. Vacuous inputs: [] → []; all-deleted → [] (rules 1 and 6 of target_spec).
