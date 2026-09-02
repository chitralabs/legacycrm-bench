# BIZ-02 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from rules
ORD-001 and ORD-002 in `legacy/order_rules.vrl` under the VRL semantics in
`legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §1/§2). No LLM output was used to
produce expectations. Derivations:

1. pct 10: ORD-001 passes (0 <= 10 <= 100); ORD-002's condition `DISC_PCT > 20` is
   false → no rule fires → success, DISC_PCT = 10.
2. Boundary at 20: ORD-002 fails only when `DISC_PCT > 20` — a strict comparison.
   20 > 20 is FALSE, so exactly 20 passes for a SALES user with no role check at all.
3. Boundary at 20.01: 20.01 > 20 is TRUE; LOOKUP for U0000001 finds a live row with
   ROLE_ID 'SALES', which is neither 'MGR' nor 'ADMIN' → both inequality conjuncts
   true → rule fails → E5002.
4. U0000002 has live ROLE_ID 'MGR' → `<> 'MGR'` conjunct false → rule passes →
   20.01 allowed. Same for U0000003 with 'ADMIN'.
5. Unknown user U0009999: §2 — LOOKUP returns '' when no live row matches; '' is
   neither 'MGR' nor 'ADMIN' → 25% fails with E5002.
6. Soft-deleted manager U0000004 (DEL_FLG='Y'): LOOKUP sees live rows only, so the
   lookup also returns '' → 25% fails with E5002 (a deleted account must not retain
   authorization power — negative/security expectation). The same user may still set
   exactly 20 because ORD-002 never triggers there (derivation 2).
7. Inactive-but-live manager U0000005 (ACTIVE_FLG='N', DEL_FLG='N'): LOOKUP filters
   on soft-delete only (§2; ACTIVE_FLG is not part of LOOKUP semantics), so the row is
   found and ROLE_ID 'MGR' authorizes 25%.
8. Range boundaries (ORD-001): `DISC_PCT >= 0 AND DISC_PCT <= 100` — inclusive.
   -0.01 violates the left bound and 100.01 the right bound → E5001; 100 satisfies
   both → allowed (for a MGR, so ORD-002 also passes).
9. Precedence: rules run in file order (§2) and ORD-001 precedes ORD-002; the modern
   service raises on the first failed check, so pct 150 by a SALES user reports E5001.
10. Messages are the literal rule messages: "Discount out of range" (E5001) and
    "Discount over 20 percent requires manager role" (E5002).
11. Purity is a target_spec requirement (rule 3): order and users equal their pre-call
    snapshots.
