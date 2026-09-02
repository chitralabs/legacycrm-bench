# VAL-01 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/opportunity_rules.vrl` under the VRL semantics in `legacy/SEMANTICS_EXCERPT.md`
(= SYSTEM_OVERVIEW.md §2). No LLM output was used to produce expectations. Derivations:

1. Compliant insert `{STAT_CD:P, STAGE_PCT:10, AMT:100, LOST_RSN:'', CLOSE_DT:'00000000'}`:
   OPP-001 pass (100≥0); OPP-002 pass (not W); OPP-003 pass (not L); OPP-004 pass (not W);
   OPP-005 not applicable (UPDATE-only); OPP-006 pass (P&10); OPP-007 pass
   (`CLOSE_DT='00000000'` first disjunct) → `[]`.
2. Won without amount: `{STAT_CD:W, STAGE_PCT:100, AMT:0, CLOSE_DT:'00000000'}` insert →
   OPP-002 fails (W and NVL(AMT,0)=0), OPP-004 fails (W and sentinel close date). Both are
   collected, in file order → codes `[E3002, E3004]`.
3. Empty-string AMT coerces to 0 (semantics: empty string in numeric comparison → 0), so the
   same record with `AMT:''` gives the same two failures.
4. Negative amount insert `{AMT:-5, STAT_CD:P, STAGE_PCT:10}` → OPP-001 fails → E3001.
5. Lost without reason `{STAT_CD:L, STAGE_PCT:0, LOST_RSN:''}` → OPP-003 fails → E3003
   (OPP-006 passes: L & 0).
6. Reopen: UPDATE with `old.STAT_CD='W'`, `record.STAT_CD='Q', STAGE_PCT:25` → OPP-005 fails
   (E3005). OPP-006 passes (Q&25).
7. Event filtering: the same record as (6) with event=INSERT does not fire OPP-005
   (WHEN UPDATE only); `OLD.STAT_CD` would be empty string anyway.
8. Stage/status mismatch `{STAT_CD:P, STAGE_PCT:25}` → OPP-006 fails → E3006.
9. OPP-007 (WARN, INSERT only): insert `{CLOSE_DT:'20250101', ...}` with today='20260901' →
   `'20250101' >= '20260901'` lexicographic is FALSE and first disjunct FALSE → rule fails →
   {code E3007, severity WARN}. A record failing only OPP-007 has `is_blocked()==False`.
10. OPP-007 not fired on UPDATE (WHEN INSERT only): same past date under UPDATE → no E3007.
11. Sentinel ordering: `CLOSE_DT='00000000'` compared with `>= today` is FALSE by sentinel
    rule, but the rule still passes via the explicit-equality disjunct (semantics rule 5).
12. Missing keys behave as empty strings: `validate({}, event="INSERT")` fires E1-style
    failures exactly for rules whose expr is FALSE under all-empty: OPP-001 passes (NVL→0≥0);
    OPP-002 passes (STAT_CD '' ≠ 'W'); OPP-003 passes ('' ≠ 'L'); OPP-004 passes; OPP-006
    fails (no disjunct true) → E3006; OPP-007: CLOSE_DT '' — `'' = '00000000'` FALSE,
    `'' >= '20260901'` lexicographic FALSE → fails → E3007 WARN. Expected codes [E3006, E3007].

13. (added 2026-09-01 after mutation triage) OPP-007 pass path with a real future date:
    `CLOSE_DT='20261231'`, today='20260901' → lexicographic `'20261231' >= '20260901'` is
    TRUE (second disjunct) → OPP-007 passes; all other rules pass as in derivation 1
    (the record differs from the compliant insert only in CLOSE_DT, and OPP-004 needs
    STAT_CD='W' to fire) → `[]`. Closes the gap that no test inserted a valid future close
    date (surviving mutant: VAL-01 migrated.py node 140, `_date_ge` sentinel guard
    `==` -> `!=`, which makes every reachable comparison return False and fires E3007 for
    all non-sentinel dates).
14. (added 2026-09-01 after mutation triage) OPP-007 boundary: `>=` is inclusive, so
    `CLOSE_DT` equal to TODAY() ('20260901' >= '20260901' lexicographic TRUE) also
    passes → `[]` (same mutant as (13), boundary arm).
