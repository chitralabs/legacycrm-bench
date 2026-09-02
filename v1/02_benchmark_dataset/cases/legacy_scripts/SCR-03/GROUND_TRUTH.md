# SCR-03 Ground-Truth Derivation

Expected values in `tests/test_acceptance.py` were derived **by hand** from
`legacy/case_escalation.crms` under the CRMScript semantics in
`legacy/SEMANTICS_EXCERPT.md` (= SYSTEM_OVERVIEW.md §4 DATEDIFF; §3 timer context;
§1 conventions). No LLM output was used to produce expectations. Unless stated,
today = "20260901". Derivations:

1. N case, OPEN_DT 20260830: DATEDIFF(20260901, 20260830) = Sep 1 − Aug 30 = 2 days
   (August has 31 days: Aug 30→Aug 31 is 1, →Sep 1 is 2) → 2 ≥ 2 → event
   {"workflow":"case_lifecycle","entity_id":<id>,"event":"auto_escalate"}.
2. N case, OPEN_DT 20260831: 1 day → 1 ≥ 2 FALSE → no event (exact boundary).
3. N case, OPEN_DT 20260901 (opened today): 0 days → no event.
4. N case, OPEN_DT 20260820: 12 days ≥ 2 → event (rule is >=, not ==).
5. A case, OPEN_DT 20260825, ESC_FLG 'N': DATEDIFF = 7 (Aug 25→Sep 1: 6 remaining August
   days + 1) → 7 ≥ 7 → event.
6. A case, OPEN_DT 20260826: 6 days → no event (exact boundary).
7. A case, OPEN_DT 20260825, ESC_FLG 'Y': second condition `c.ESC_FLG <> 'Y'` FALSE →
   no event (already escalated; negative expectation).
8. A case, ESC_FLG '' (blank counts as not escalated, §1): 7 days → event.
9. N case with ESC_FLG 'Y', OPEN_DT 20260820: the N rule tests only STAT_CD and
   DATEDIFF — ESC_FLG is irrelevant → event still emitted (subtle asymmetry vs rule 3).
10. Sentinel rule: OPEN_DT '00000000' → DATEDIFF = 0 by definition → 0 ≥ 2 FALSE →
    never overdue, for both N and A rules. Empty/missing OPEN_DT behaves the same
    (spec rule 5).
11. Future OPEN_DT 20260905: DATEDIFF = −4 → no event.
12. Soft-deleted N case, OPEN_DT 20260820: FOR EACH scans live rows only → no event.
13. Statuses P/R/X with OPEN_DT 20260801 (31 days): neither IF matches → no events.
14. Calendar arithmetic across a month boundary: today 20260301, N case OPEN_DT 20260227:
    2026 is not a leap year (2026/4 not integral) → Feb has 28 days → Feb 27→28 is 1,
    →Mar 1 is 2 → 2 ≥ 2 → event. String/naive numeric subtraction (20260301−20260227=74)
    or day-of-month subtraction (1−27=−26) would both misfire elsewhere; only real date
    math yields 2.
15. Ordering: input cases [C00000009 (N, 20260820), C00000001 (A, 20260801, ESC 'N')] →
    both overdue; FOR EACH iterates by primary key ascending → events for
    C00000001 then C00000009.
16. At most one event per case: a single N case matches only the first IF (STAT_CD can't
    be both 'N' and 'A'); the events list for one overdue case has length 1.
