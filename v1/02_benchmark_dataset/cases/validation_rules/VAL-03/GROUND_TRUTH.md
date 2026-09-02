# VAL-03 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/order_rules.vrl` under the VRL semantics in `legacy/SEMANTICS_EXCERPT.md`
(= SYSTEM_OVERVIEW.md §2; LOOKUP "returns matching column value or empty string if no live
row") plus the soft-delete convention (§1). No LLM output was used.

Test fixture tables: USR_MASTER = U0000001/MGR (live), U0000002/SLS (live), U0000003/MGR
(DEL_FLG='Y'), U0000004/ADMIN (live); PROD_MASTER = P00000001 ACTIVE_FLG='Y' (live),
P00000002 ACTIVE_FLG='N' (live), P00000003 ACTIVE_FLG='Y' but DEL_FLG='Y'.

1. Compliant header insert (DISC_PCT 10, STAT_CD 'E'): ORD-001 passes (0≤10≤100); ORD-002 and
   ORD-003 are UPDATE-only → `[]`.
2. ORD-001 range: DISC_PCT 101 → 101 ≤ 100 FALSE → E5001; DISC_PCT -1 → -1 ≥ 0 FALSE → E5001.
3. Blank DISC_PCT coerces to 0 (empty-numeric convention) → 0≥0 and 0≤100 → ORD-001 passes;
   0 > 20 FALSE so ORD-002 also passes on UPDATE.
4. ORD-002, MGR owner: UPDATE, DISC_PCT 25, OWNER_UID U0000001 → LOOKUP returns 'MGR' →
   the conjunct role<>'MGR' is FALSE → NOT(...) TRUE → passes.
5. ORD-002, ADMIN owner U0000004 → LOOKUP 'ADMIN' → role<>'ADMIN' FALSE → passes.
6. ORD-002, SLS owner U0000002 → 'SLS' is neither MGR nor ADMIN and 25 > 20 → fails → E5002.
7. ORD-002, unknown owner U0000099 → no row → LOOKUP returns '' → '' <> 'MGR' and
   '' <> 'ADMIN' both TRUE → fails → E5002 (documented consequence: unknown user's role is "").
8. ORD-002, soft-deleted MGR U0000003 → LOOKUP ignores DEL_FLG='Y' rows → returns '' →
   fails → E5002.
9. ORD-002 boundary: DISC_PCT exactly 20 → 20 > 20 FALSE → passes even for SLS owner.
10. ORD-002 event filter: WHEN UPDATE only → the SLS/25 record under INSERT yields no E5002.
11. ORD-003: old STAT_CD 'I', new 'S' → 'S'<>'I' and 'S'<>'X' → conjunction TRUE →
    NOT(...) FALSE → fails → E5003. New 'X' → 'X'<>'X' FALSE → passes (cancel allowed).
    New 'I' → 'I'<>'I' FALSE → passes (staying invoiced allowed).
12. ORD-004: QTY 0 → 0 > 0 FALSE → E5004 (line, INSERT or UPDATE). QTY 3 passes.
13. ORD-005 (INSERT only): P00000001 live+active → LOOKUP 'Y' → passes. P00000002 live but
    ACTIVE_FLG 'N' → LOOKUP 'N' ≠ 'Y' → E5005. P00000003 soft-deleted → LOOKUP '' → E5005.
    Missing P00000099 → LOOKUP '' → E5005.
14. ORD-005 event filter: WHEN INSERT only → an UPDATE of a line with a missing product
    yields no E5005.
15. Collect-all in file order (line INSERT, QTY 0, product P00000002): ORD-004 fails then
    ORD-005 fails → codes exactly [E5004, E5005].
16. Header rules never run for table="ORD_LINE" and vice versa (rules are ON one table);
    e.g. a line record never yields E5001.

17. (added 2026-09-01 after mutation triage) Spec'd default event: target_spec.md fixes the
    signature `validate(record, old=None, event="INSERT", tables=None, table=...)`, so a
    call that omits `event` must behave as INSERT and run the INSERT-only ORD-005. With
    the inactive product P00000002 (ACTIVE_FLG='N' → LOOKUP returns 'N' ≠ 'Y', derivation
    13) the omitted-event call yields exactly [E5005]. Closes the gap that every prior
    test passed `event` positionally (surviving mutant: VAL-03 migrated.py node 55,
    default 'INSERT' -> 'INSERT_X', which silently skips E5005 on defaulted calls).
18. (added 2026-09-01 after mutation triage) ORD-001 inclusive upper boundary: the rule is
    `DISC_PCT >= 0 AND DISC_PCT <= 100`, so DISC_PCT exactly 100 passes; ORD-002/ORD-003
    are UPDATE-only → a compliant INSERT with DISC_PCT=100 yields `[]`. Closes the gap
    that only 101, -1, and 20 were probed (surviving mutant: VAL-03 migrated.py node 245,
    `disc <= 100` -> `disc < 100`, which rejects the legal boundary value).
